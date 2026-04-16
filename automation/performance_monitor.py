# -*- coding: utf-8 -*-
"""
RealE Tube - Performance Monitor
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from database.db import DatabaseManager
from automation.youtube_research import YouTubeResearcher
from automation.youtube_uploader import YouTubeUploader
from automation.quota_manager import QuotaManager
from datetime import datetime, timedelta
from typing import Dict, List
import json

class PerformanceMonitor:
    def __init__(self, db: DatabaseManager, youtube_researcher: YouTubeResearcher,
                 youtube_uploader: YouTubeUploader, config: Dict):
        """
        Initialize performance monitor
        
        Args:
            db: Database manager instance
            youtube_researcher: YouTube research instance for getting metrics
            youtube_uploader: YouTube uploader for deleting underperforming videos
            config: Configuration dict with thresholds
        """
        self.db = db
        self.youtube = youtube_researcher
        self.uploader = youtube_uploader
        self.config = config
    
    def check_all_videos(self) -> Dict:
        """
        Check all videos that need monitoring.
        Handles offline gaps - checks ANY video past its time threshold.
        
        Returns:
            Dict with summary of actions taken
        """
        summary = {
            'checked': 0,
            'successful': 0,
            'retrying': 0,
            'abandoned': 0,
            'still_monitoring': 0,
            'skipped_too_early': 0
        }
        
        # Refuse to monitor anything when quota is exhausted — prevents
        # hundreds of quotaExceeded errors spamming the log.
        qm = QuotaManager.get_instance()
        if qm.is_exhausted():
            summary['quota_exhausted'] = True
            return summary

        # Get videos that need checking
        videos = self.db.get_videos_for_monitoring()

        for video in videos:
            # Check if enough time has passed since upload
            if not self._should_check_now(video):
                summary['skipped_too_early'] += 1
                continue

            # Bail immediately if quota was exhausted mid-loop.
            if qm.is_exhausted():
                summary['quota_exhausted'] = True
                break

            # This video passed its check time - process it now
            summary['checked'] += 1

            upload_date = datetime.fromisoformat(video['upload_date'])
            hours_since_upload = (datetime.now() - upload_date).total_seconds() / 3600

            print(f"Checking video: {video['title_used'][:40]}... "
                  f"(Attempt {video['attempt_number']}, {hours_since_upload:.1f}h since upload)")

            # Get current performance
            metrics = self.youtube.get_video_performance(video['youtube_video_id'])
            
            if not metrics:
                print(f"Could not get metrics for video {video['id']}")
                continue
            
            # Update database with metrics
            self.db.update_video_metrics(video['id'], metrics)
            
            # Check if meets thresholds
            performance = self._check_performance(metrics)
            
            if performance['success']:
                # Video is performing well!
                self.db.mark_as_success(video['id'])
                self._update_keyword_stats(video, metrics, success=True)
                summary['successful'] += 1
                print(f"✓ Video {video['id']} marked as SUCCESS - "
                      f"{metrics['views']} views, "
                      f"{(metrics['views']/metrics['impressions']*100):.1f}% CTR")
                
            elif performance['should_retry']:
                # Video underperforming - retry if attempts remaining
                if video['attempt_number'] < video['max_attempts']:
                    # Delete and retry
                    self.uploader.delete_video(video['youtube_video_id'])
                    self.db.mark_for_retry(video['id'], performance['reason'])
                    self._update_keyword_stats(video, metrics, success=False)
                    summary['retrying'] += 1
                    print(f"⟳ Video {video['id']} marked for RETRY - {performance['reason']}")
                else:
                    # Max attempts reached - abandon
                    self.uploader.delete_video(video['youtube_video_id'])
                    self.db.mark_as_abandoned(video['id'])
                    self._update_keyword_stats(video, metrics, success=False)
                    summary['abandoned'] += 1
                    print(f"✗ Video {video['id']} ABANDONED after {video['attempt_number']} attempts")
            else:
                # Still within acceptable range, keep monitoring
                summary['still_monitoring'] += 1
        
        return summary
    
    def _should_check_now(self, video: Dict) -> bool:
        """
        Determine if enough time has passed to check video
        Works correctly even if PC was offline during the check window.
        
        Args:
            video: Video dict from database
            
        Returns:
            True if should check now (time threshold passed)
        """
        upload_date = datetime.fromisoformat(video['upload_date'])
        now = datetime.now()
        hours_since_upload = (now - upload_date).total_seconds() / 3600
        
        attempt = video['attempt_number']
        
        # Get check timing from config
        first_check_hours = self.config['retry']['first_check_hours']
        second_check_hours = self.config['retry']['second_check_hours']
        
        # Determine required hours based on attempt
        # This works even if PC was off - just checks elapsed time
        if attempt == 1:
            required_hours = first_check_hours
        elif attempt == 2:
            required_hours = second_check_hours
        else:
            required_hours = 72  # Final attempt gets 72 hours
        
        # True if enough time has elapsed, regardless of when we last checked
        return hours_since_upload >= required_hours
    
    def _check_performance(self, metrics: Dict) -> Dict:
        """
        Check if video meets performance thresholds.

        Logic:
        - A video that hits the view threshold is ALWAYS marked as success,
          regardless of CTR/engagement.  High-view videos must never be deleted.
        - CTR is only evaluated when real impression data is available
          (YouTube Data API v3 does not provide impressions, so CTR is
          skipped unless the caller supplies a positive impressions value).
        - Engagement is evaluated but treated as advisory when views are
          above 2x the minimum threshold.

        Args:
            metrics: Current video metrics

        Returns:
            Dict with success, should_retry, and reason
        """
        min_views = self.config['performance']['min_views']
        min_ctr = self.config['performance']['min_ctr']
        min_engagement = self.config['performance']['min_engagement']
        engagement_required = self.config['performance'].get('engagement_required', False)
        view_protection = self.config['performance'].get('view_protection_multiplier', 2.0)

        views = metrics.get('views', 0)
        impressions = metrics.get('impressions', 0)
        likes = metrics.get('likes', 0)
        comments = metrics.get('comments', 0)

        # Engagement rate
        engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0

        # CTR — only meaningful when we have real impression data
        has_real_impressions = impressions > 0
        ctr = (views / impressions * 100) if has_real_impressions else 0

        # ── View protection safeguard ─────────────────────────────
        # Videos above (min_views * multiplier) are NEVER deleted.
        if views >= min_views * view_protection:
            return {
                'success': True,
                'should_retry': False,
                'reason': f'High performer ({views} views, {engagement_rate:.1f}% engagement)'
            }

        # ── Standard threshold check ─────────────────────────────
        meets_views = views >= min_views
        # Only require CTR when we can actually measure it
        meets_ctr = ctr >= min_ctr if has_real_impressions else True
        # Engagement only matters if the user turned it on
        meets_engagement = engagement_rate >= min_engagement if engagement_required else True

        if meets_views and meets_ctr and meets_engagement:
            return {
                'success': True,
                'should_retry': False,
                'reason': 'Performance meets all thresholds'
            }

        # ── Views met but engagement low — keep monitoring ────────
        if meets_views and not meets_engagement:
            return {
                'success': False,
                'should_retry': False,
                'reason': f'Views OK ({views}) but engagement low ({engagement_rate:.1f}%) — still monitoring'
            }

        # ── Underperforming — build reason ────────────────────────
        reasons = []
        if not meets_views:
            reasons.append(f"views ({views} < {min_views})")
        if has_real_impressions and not meets_ctr:
            reasons.append(f"CTR ({ctr:.1f}% < {min_ctr}%)")
        if engagement_required and not meets_engagement:
            reasons.append(f"engagement ({engagement_rate:.1f}% < {min_engagement}%)")

        reason = "Underperforming: " + ", ".join(reasons)

        return {
            'success': False,
            'should_retry': True,
            'reason': reason
        }
    
    def _update_keyword_stats(self, video: Dict, metrics: Dict, success: bool):
        """Update keyword performance statistics"""
        try:
            keywords = json.loads(video['keywords_targeted'])
            
            for keyword in keywords:
                self.db.update_keyword_performance(
                    keyword=keyword,
                    video_success=success,
                    metrics={
                        'views': metrics.get('views', 0),
                        'ctr': (metrics.get('views', 0) / metrics.get('impressions', 1) * 100) if metrics.get('impressions', 1) > 0 else 0,
                        'engagement_rate': ((metrics.get('likes', 0) + metrics.get('comments', 0)) / metrics.get('views', 1) * 100) if metrics.get('views', 1) > 0 else 0
                    }
                )
        except Exception as e:
            print(f"Error updating keyword stats: {e}")
    
    def get_monitoring_summary(self) -> str:
        """Get human-readable summary of monitoring status"""
        videos = self.db.get_videos_for_monitoring()
        
        if not videos:
            return "No videos currently being monitored"
        
        summary_lines = [f"Monitoring {len(videos)} videos:"]
        
        for video in videos:
            upload_date = datetime.fromisoformat(video['upload_date'])
            hours_ago = (datetime.now() - upload_date).total_seconds() / 3600
            
            summary_lines.append(
                f"  - {video['title_used'][:50]}... "
                f"(Attempt {video['attempt_number']}, "
                f"{hours_ago:.1f}h ago, "
                f"{video['views']} views, "
                f"{video['ctr']:.1f}% CTR)"
            )
        
        return "\n".join(summary_lines)
