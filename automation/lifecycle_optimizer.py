# -*- coding: utf-8 -*-
"""
RealE Tube - Lifecycle Optimizer
Automatically reoptimizes underperforming videos with new metadata
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from database.db import DatabaseManager
from automation.keyword_generator import KeywordGenerator
from automation.youtube_research import YouTubeResearcher
from automation.youtube_uploader import YouTubeUploader
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class LifecycleOptimizer:
    """
    Automatically detect and reoptimize underperforming videos.

    Triggers on:
    - Low CTR (< 3%)
    - Low engagement (< 2%)
    - Videos older than 30 days not receiving views
    """

    def __init__(self, youtube_service=None, ai_key: str = None):
        """
        Initialize lifecycle optimizer

        Args:
            youtube_service: Authenticated YouTube service
            ai_key: Anthropic API key for keyword generation
        """
        self.db = DatabaseManager()
        self.youtube_service = youtube_service
        self.ai_key = ai_key

        # Initialize optional components
        self.youtube_uploader = YouTubeUploader(youtube_service=youtube_service) if youtube_service else None
        self.keyword_gen = KeywordGenerator(ai_key) if ai_key else None
        self.youtube_researcher = YouTubeResearcher(youtube_service=youtube_service) if youtube_service else None

    def find_reoptimization_candidates(self, force_all: bool = False) -> List[Dict]:
        """
        Identify videos that should be reoptimized

        Args:
            force_all: If True, return all videos below thresholds
                      If False, only return videos not recently reoptimized

        Returns:
            List of candidate video dicts
        """
        try:
            videos = self.db.get_all_videos()
        except Exception:
            return []

        candidates = []

        for v in videos:
            # Skip videos without YouTube ID (not yet uploaded)
            if not v.get('youtube_video_id'):
                continue

            views = v.get('views') or 0
            ctr = self._safe_float(v.get('ctr'), 0)
            engagement = self._safe_float(v.get('engagement_rate'), 0)

            # Skip if no data
            if views == 0:
                continue

            # Check thresholds
            is_low_ctr = ctr < 3.0
            is_low_engagement = engagement < 2.0
            is_stale_evergreen = self._is_stale_evergreen(v)

            if is_low_ctr or is_low_engagement or is_stale_evergreen:
                reason = []
                if is_low_ctr:
                    reason.append(f"CTR {ctr:.1f}%")
                if is_low_engagement:
                    reason.append(f"Engagement {engagement:.1f}%")
                if is_stale_evergreen:
                    reason.append("Stale evergreen (no recent views)")

                v['reopt_reasons'] = reason
                candidates.append(v)

        return candidates

    def auto_reoptimize_video(self, video_id: int, new_keywords: List[str] = None) -> Optional[Dict]:
        """
        Automatically generate and apply new metadata to a video

        Args:
            video_id: Video ID to reoptimize
            new_keywords: Override keywords (if None, generate from original description)

        Returns:
            Dict with old/new metadata, or None if failed
        """
        if not self.keyword_gen or not self.youtube_uploader:
            raise ValueError("Keyword generator and YouTube uploader required for reoptimization")

        # Get video
        video = self.db.get_video(video_id)
        if not video:
            return None

        # Prepare changes
        original_desc = video.get('original_description', '')
        old_title = video.get('title_used', '')
        old_description = video.get('description_used', '')

        # Generate new metadata
        keywords = new_keywords or self.keyword_gen.generate_keywords(original_desc, 'aggressive')
        new_title = self.keyword_gen.generate_title(original_desc, [], attempt=2)
        new_description = self.keyword_gen.generate_description(original_desc, keywords, [], attempt=2)

        # Apply to YouTube
        success = self.youtube_uploader.update_video_metadata(
            video['youtube_video_id'],
            title=new_title,
            description=new_description,
            tags=keywords
        )

        if success:
            # Track the reoptimization
            self.db.add_reopt_record(
                video_id,
                old_title,
                new_title,
                video.get('ctr', 0),
                video.get('engagement_rate', 0),
                reason="Automated lifecycle reoptimization"
            )

            return {
                'video_id': video_id,
                'old_title': old_title,
                'new_title': new_title,
                'old_ctr': video.get('ctr'),
                'new_keywords': keywords
            }

        return None

    def batch_reoptimize(self, max_videos: int = 5, dry_run: bool = True) -> Dict:
        """
        Reoptimize top N underperforming videos

        Args:
            max_videos: Maximum videos to reoptimize
            dry_run: If True, don't apply changes (just show what would happen)

        Returns:
            Summary of changes
        """
        candidates = self.find_reoptimization_candidates()

        # Sort by views (descending) to prioritize videos with traffic
        candidates.sort(key=lambda x: x.get('views', 0), reverse=True)

        results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'changes': []
        }

        for video in candidates[:max_videos]:
            results['attempted'] += 1

            if dry_run:
                results['changes'].append({
                    'video_id': video['id'],
                    'title': video.get('title_used', ''),
                    'reasons': video.get('reopt_reasons', []),
                    'action': 'WOULD REOPTIMIZE'
                })
                results['successful'] += 1
            else:
                try:
                    result = self.auto_reoptimize_video(video['id'])
                    if result:
                        results['successful'] += 1
                        results['changes'].append(result)
                    else:
                        results['failed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    print(f"Error reoptimizing video {video['id']}: {e}")

        return results

    def _is_stale_evergreen(self, video: Dict) -> bool:
        """Check if evergreen content is stale (no views in 7 days)"""
        try:
            age_days = self._get_age_days(video)
            views = video.get('views', 0)
            last_checked = video.get('last_checked')

            if not last_checked or age_days is None:
                return False

            # Only flag evergreen (30+ days old) with no recent views
            if age_days < 30:
                return False

            if views == 0:
                return True

            # Check if any views in last 7 days
            last_checked_dt = self._parse_date(last_checked)
            if last_checked_dt and (datetime.now() - last_checked_dt).days > 7:
                return True

            return False
        except Exception:
            return False

    @staticmethod
    def _get_age_days(video: Dict) -> Optional[int]:
        """Get video age in days"""
        dt = LifecycleOptimizer._parse_date(video.get('created_at') or video.get('upload_date'))
        if dt:
            return (datetime.now() - dt).days
        return None

    @staticmethod
    def _parse_date(value):
        """Parse ISO date string"""
        if not value:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        return None

    @staticmethod
    def _safe_float(value, default=0.0) -> float:
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default
