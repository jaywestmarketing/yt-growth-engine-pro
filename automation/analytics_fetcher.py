# -*- coding: utf-8 -*-
"""
RealE Tube - Advanced Analytics Fetcher
Retrieves detailed YouTube insights: traffic sources, geography, device types
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from database.db import DatabaseManager
from typing import Dict, List, Optional
import json


class AnalyticsFetcher:
    """
    Fetch advanced YouTube analytics beyond basic views/likes/comments.

    Note: YouTube Data API v3 has limited analytics.
    For full analytics, YouTube Analytics API would be needed (requires OAuth).
    This class provides data enrichment from available endpoints.
    """

    def __init__(self, youtube_service=None):
        """
        Initialize analytics fetcher

        Args:
            youtube_service: Authenticated YouTube service
        """
        self.youtube = youtube_service
        self.db = DatabaseManager()

    def get_channel_statistics(self) -> Optional[Dict]:
        """
        Get channel-level statistics

        Returns:
            Dict with channel stats (subscribers, view count, video count)
        """
        if not self.youtube:
            return None

        try:
            response = self.youtube.channels().list(
                part='statistics,snippet',
                mine=True
            ).execute()

            if not response.get('items'):
                return None

            channel = response['items'][0]
            stats = channel.get('statistics', {})

            return {
                'channel_name': channel['snippet']['title'],
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'hidden_subscriber_count': stats.get('hiddenSubscriberCount', False)
            }

        except Exception as e:
            print(f"Error fetching channel statistics: {e}")
            return None

    def get_video_insights(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed insights for a specific video

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with views, likes, comments, engagement
        """
        if not self.youtube:
            return None

        try:
            response = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=video_id
            ).execute()

            if not response.get('items'):
                return None

            video = response['items'][0]
            stats = video['statistics']

            duration_iso = video['contentDetails']['duration']
            duration_sec = self._parse_iso_duration(duration_iso)

            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))

            engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0

            return {
                'video_id': video_id,
                'title': video['snippet']['title'],
                'views': views,
                'likes': likes,
                'comments': comments,
                'engagement_rate': engagement_rate,
                'duration_seconds': duration_sec,
                'published_at': video['snippet']['publishedAt'],
                'like_rate': (likes / views * 100) if views > 0 else 0,
                'comment_rate': (comments / views * 100) if views > 0 else 0
            }

        except Exception as e:
            print(f"Error fetching video insights: {e}")
            return None

    def analyze_competitor_performance(self, competitor_ids: List[str]) -> Dict:
        """
        Analyze performance across competitor videos

        Args:
            competitor_ids: List of YouTube video IDs from competitors

        Returns:
            Dict with aggregated metrics and benchmarks
        """
        if not self.youtube or not competitor_ids:
            return {}

        metrics = {
            'avg_views': 0,
            'avg_likes': 0,
            'avg_comments': 0,
            'avg_engagement': 0,
            'avg_like_rate': 0,
            'median_duration': 0,
            'total_videos': len(competitor_ids),
            'videos': []
        }

        durations = []
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_engagement = 0

        for video_id in competitor_ids:
            try:
                insights = self.get_video_insights(video_id)
                if insights:
                    metrics['videos'].append(insights)
                    total_views += insights['views']
                    total_likes += insights['likes']
                    total_comments += insights['comments']
                    total_engagement += insights['engagement_rate']
                    durations.append(insights['duration_seconds'])
            except Exception:
                continue

        # Calculate averages
        n = len(metrics['videos'])
        if n > 0:
            metrics['avg_views'] = total_views / n
            metrics['avg_likes'] = total_likes / n
            metrics['avg_comments'] = total_comments / n
            metrics['avg_engagement'] = total_engagement / n
            metrics['avg_like_rate'] = (total_likes / max(total_views, 1)) * 100

            if durations:
                durations.sort()
                metrics['median_duration'] = durations[n // 2]

        return metrics

    def suggest_improvements_from_competitors(self, your_video_id: str,
                                              competitor_ids: List[str]) -> List[str]:
        """
        Compare your video to competitors and suggest improvements

        Args:
            your_video_id: Your video ID
            competitor_ids: Competitor video IDs to compare against

        Returns:
            List of improvement suggestions
        """
        your_insights = self.get_video_insights(your_video_id)
        if not your_insights:
            return []

        comp_metrics = self.analyze_competitor_performance(competitor_ids)
        if not comp_metrics['avg_views']:
            return []

        suggestions = []

        # View rate comparison
        if your_insights['views'] < comp_metrics['avg_views'] * 0.5:
            suggestions.append(
                f"Your video has {your_insights['views']} views vs. "
                f"competitor average of {comp_metrics['avg_views']:.0f}. "
                f"Consider improving title/thumbnail or promoting with similar keywords."
            )

        # Engagement comparison
        if your_insights['engagement_rate'] < comp_metrics['avg_engagement'] * 0.7:
            suggestions.append(
                f"Your engagement rate is {your_insights['engagement_rate']:.1f}% vs. "
                f"competitor average of {comp_metrics['avg_engagement']:.1f}%. "
                f"Try adding CTAs, timestamps, or community engagement."
            )

        # Duration comparison
        if comp_metrics['median_duration'] > 0:
            your_duration = your_insights['duration_seconds']
            median_duration = comp_metrics['median_duration']
            ratio = your_duration / max(median_duration, 1)

            if ratio < 0.7:
                suggestions.append(
                    f"Your video is {your_duration/60:.0f}min vs. "
                    f"competitor median of {median_duration/60:.0f}min. "
                    f"Longer-form content may perform better in your niche."
                )
            elif ratio > 1.5:
                suggestions.append(
                    f"Your video is {your_duration/60:.0f}min vs. "
                    f"competitor median of {median_duration/60:.0f}min. "
                    f"Consider shorter, more focused content."
                )

        return suggestions

    def get_performance_summary(self) -> Dict:
        """
        Get summary statistics across all your videos

        Returns:
            Dict with aggregate stats
        """
        try:
            videos = self.db.get_all_videos()
        except Exception:
            return {}

        total_views = 0
        total_likes = 0
        total_comments = 0
        total_engagement = 0
        video_count = 0

        for v in videos:
            if v.get('views', 0) > 0:
                total_views += v.get('views', 0)
                total_likes += v.get('likes', 0)
                total_comments += v.get('comments', 0)
                total_engagement += v.get('engagement_rate', 0)
                video_count += 1

        return {
            'total_videos_tracked': video_count,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_views_per_video': total_views / max(video_count, 1),
            'avg_engagement_rate': total_engagement / max(video_count, 1),
            'overall_like_rate': (total_likes / max(total_views, 1)) * 100,
            'overall_comment_rate': (total_comments / max(total_views, 1)) * 100
        }

    # ── Helper methods ────────────────────────────────────────────

    @staticmethod
    def _parse_iso_duration(duration_str: str) -> int:
        """
        Parse ISO 8601 duration string to seconds

        Args:
            duration_str: Duration like 'PT1H23M45S'

        Returns:
            Duration in seconds
        """
        import re

        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds
