# -*- coding: utf-8 -*-
"""
RealE Tube - YouTube Competitor Research
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from googleapiclient.discovery import build
from automation.google_auth import GoogleAuthHelper
from automation.quota_manager import QuotaManager
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
import json

class YouTubeResearcher:
    def __init__(self, credentials_path: str = None, youtube_service = None):
        """
        Initialize YouTube API client
        
        Args:
            credentials_path: Path to OAuth credentials JSON (optional if youtube_service provided)
            youtube_service: Pre-authenticated YouTube service (optional)
        """
        if youtube_service:
            self.youtube = youtube_service
        elif credentials_path:
            auth_helper = GoogleAuthHelper(credentials_path)
            self.youtube = auth_helper.get_youtube_service()
        else:
            raise ValueError("Must provide either credentials_path or youtube_service")
    
    def search_competitors(self, keywords: List[str], min_likes: int = 150,
                          max_results: int = 20,
                          max_age_days: Optional[int] = None) -> List[Dict]:
        """
        Search for competitor videos with minimum likes

        Args:
            keywords: List of keywords to search for
            min_likes: Minimum number of likes required
            max_results: Maximum number of videos to return
            max_age_days: If set and > 0, only consider videos uploaded within
                          this many days. Passed to the YouTube search as
                          `publishedAfter` to let the API do the filtering,
                          which saves quota and avoids ranking stale clips.

        Returns:
            List of video information dicts
        """

        all_videos = []
        qm = QuotaManager.get_instance()

        # Build the `publishedAfter` filter once so every keyword search uses
        # the same cutoff. YouTube expects RFC 3339 (UTC, Z-suffixed).
        published_after = None
        if max_age_days and max_age_days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(days=int(max_age_days))
            published_after = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')

        for keyword in keywords[:3]:  # Search top 3 keywords to save quota
            if qm.is_exhausted():
                print(f"Skipping keyword '{keyword}' — YouTube API quota exhausted.")
                continue
            # search.list costs 100 units — refuse early if we can't afford it
            if not qm.can_spend('search.list'):
                print(f"Skipping keyword '{keyword}' — insufficient quota remaining.")
                continue
            try:
                # Search for videos
                if not qm.spend('search.list'):
                    continue
                search_kwargs = dict(
                    q=keyword,
                    part='id,snippet',
                    type='video',
                    maxResults=min(50, max_results * 3),  # Get extra to filter
                    order='viewCount',
                    relevanceLanguage='en'
                )
                if published_after:
                    search_kwargs['publishedAfter'] = published_after
                search_response = self.youtube.search().list(**search_kwargs).execute()

                video_ids = [item['id']['videoId'] for item in search_response['items']]

                # Get detailed stats
                if not qm.spend('videos.list'):
                    continue
                videos_response = self.youtube.videos().list(
                    part='statistics,snippet',
                    id=','.join(video_ids)
                ).execute()
                
                for video in videos_response['items']:
                    stats = video['statistics']
                    likes = int(stats.get('likeCount', 0))
                    
                    if likes >= min_likes:
                        all_videos.append({
                            'video_id': video['id'],
                            'title': video['snippet']['title'],
                            'description': video['snippet'].get('description', ''),
                            'tags': video['snippet'].get('tags', []),
                            'views': int(stats.get('viewCount', 0)),
                            'likes': likes,
                            'comments': int(stats.get('commentCount', 0)),
                            'published_at': video['snippet']['publishedAt']
                        })
                
            except Exception as e:
                if qm.handle_api_error(e):
                    continue
                print(f"Error searching keyword '{keyword}': {e}")
                continue
        
        # Sort by likes and return top results
        all_videos.sort(key=lambda x: x['likes'], reverse=True)
        return all_videos[:max_results]
    
    def extract_tags_from_competitors(self, competitor_videos: List[Dict]) -> List[str]:
        """
        Extract all unique tags from competitor videos
        
        Args:
            competitor_videos: List of competitor video dicts
            
        Returns:
            List of unique tags
        """
        all_tags = []
        
        for video in competitor_videos:
            tags = video.get('tags', [])
            all_tags.extend(tags)
        
        # Deduplicate and convert to lowercase
        unique_tags = list(set(tag.lower() for tag in all_tags))
        
        return unique_tags
    
    def analyze_title_patterns(self, competitor_videos: List[Dict]) -> Dict:
        """
        Analyze patterns in successful titles
        
        Args:
            competitor_videos: List of competitor video dicts
            
        Returns:
            Dict with pattern analysis
        """
        titles = [v['title'] for v in competitor_videos]
        
        analysis = {
            'avg_length': sum(len(t) for t in titles) / len(titles) if titles else 0,
            'common_words': self._get_common_words(titles),
            'has_numbers': sum(1 for t in titles if any(c.isdigit() for c in t)) / len(titles) if titles else 0,
            'has_question': sum(1 for t in titles if '?' in t) / len(titles) if titles else 0,
            'all_titles': titles
        }
        
        return analysis
    
    def _get_common_words(self, titles: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most common words across titles"""
        from collections import Counter
        
        # Tokenize and count
        words = []
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'on', 'in', 'at', 'to', 'for', 'of', 'and', 'or', 'how', 'what', 'why', 'when'}
        
        for title in titles:
            words.extend([w.lower() for w in title.split() if w.lower() not in stop_words and len(w) > 2])
        
        return Counter(words).most_common(top_n)
    
    def get_video_performance(self, video_id: str) -> Dict:
        """
        Get current performance metrics for a video

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with current metrics
        """
        qm = QuotaManager.get_instance()
        if not qm.spend('videos.list'):
            return None

        try:
            response = self.youtube.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()

            if not response['items']:
                return None

            video = response['items'][0]
            stats = video['statistics']

            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))

            # YouTube Data API v3 does not expose impressions directly.
            # Store 0 so the caller knows it is unavailable rather than
            # using a fabricated number that produces a fake CTR.
            return {
                'views': views,
                'likes': likes,
                'comments': comments,
                'impressions': 0,
                'title': video['snippet']['title']
            }

        except Exception as e:
            if qm.handle_api_error(e):
                return None
            print(f"Error getting video performance: {e}")
            return None
