# -*- coding: utf-8 -*-
"""
RealE Tube - Standalone Comment Bot
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from automation.google_auth import GoogleAuthHelper
from automation.keyword_generator import KeywordGenerator
from automation.youtube_research import YouTubeResearcher
from automation.comment_bot import CommentBot
import json
import time
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlparse, parse_qs


def _load_competitor_max_age_days(default: int = 7) -> int:
    """Read the competitor age filter from config.json, falling back to 7."""
    try:
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        if not config_path.exists():
            return default
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return int(cfg.get("keywords", {}).get("competitor_max_age_days", default))
    except Exception:
        return default

class StandaloneCommentBot:
    def __init__(self, youtube_service, ai_generator: KeywordGenerator):
        """
        Initialize standalone comment bot for manual use
        
        Args:
            youtube_service: Authenticated YouTube API service
            ai_generator: AI keyword generator for creating comments
        """
        self.youtube = youtube_service
        self.ai_generator = ai_generator
        self.comment_bot = CommentBot(youtube_service, ai_generator)
        self.researcher = YouTubeResearcher(youtube_service=youtube_service)
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID or None
        """
        try:
            parsed = urlparse(url)
            
            # youtube.com/watch?v=VIDEO_ID
            if 'youtube.com' in parsed.netloc:
                query_params = parse_qs(parsed.query)
                if 'v' in query_params:
                    return query_params['v'][0]
            
            # youtu.be/VIDEO_ID
            elif 'youtu.be' in parsed.netloc:
                return parsed.path.strip('/')
            
            return None
            
        except Exception as e:
            print(f"Error extracting video ID: {e}")
            return None
    
    def analyze_video_and_find_similar(self, video_url: str, max_results: int = 20) -> List[Dict]:
        """
        Analyze a video and find similar videos to comment on
        
        Args:
            video_url: URL of the video to analyze
            max_results: Number of similar videos to find
            
        Returns:
            List of similar video dicts
        """
        video_id = self.extract_video_id(video_url)
        
        if not video_id:
            print("Invalid YouTube URL")
            return []
        
        try:
            # Get video info
            response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not response['items']:
                print("Video not found")
                return []
            
            video_info = response['items'][0]['snippet']
            title = video_info['title']
            description = video_info.get('description', '')
            tags = video_info.get('tags', [])
            
            print(f"Analyzing video: {title}")
            
            # Generate keywords from title and description
            content = f"{title} {description}"
            keywords = self.ai_generator.generate_keywords(content, "Medium")
            
            print(f"Generated {len(keywords)} keywords: {', '.join(keywords[:5])}...")
            
            # Search for similar videos — respect the user's age filter
            # (default 7 days) so we don't surface stale videos.
            similar_videos = self.researcher.search_competitors(
                keywords,
                min_likes=50,  # Lower threshold for broader results
                max_results=max_results,
                max_age_days=_load_competitor_max_age_days(),
            )
            
            # Remove the original video from results
            similar_videos = [v for v in similar_videos if v['video_id'] != video_id]
            
            print(f"Found {len(similar_videos)} similar videos")
            
            return similar_videos
            
        except Exception as e:
            print(f"Error analyzing video: {e}")
            return []
    
    def get_channel_videos(self, channel_url: str, max_results: int = 50) -> List[Dict]:
        """
        Get recent videos from a YouTube channel
        
        Args:
            channel_url: YouTube channel URL or ID
            max_results: Number of videos to retrieve
            
        Returns:
            List of video dicts
        """
        try:
            # Extract channel ID from URL
            channel_id = self._extract_channel_id(channel_url)
            
            if not channel_id:
                print("Invalid channel URL")
                return []
            
            # Get channel's uploads playlist
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                print("Channel not found")
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                playlist_response = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                for item in playlist_response['items']:
                    video_info = item['snippet']
                    videos.append({
                        'video_id': video_info['resourceId']['videoId'],
                        'title': video_info['title'],
                        'description': video_info.get('description', ''),
                        'published_at': video_info['publishedAt']
                    })
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            print(f"Retrieved {len(videos)} videos from channel")
            
            return videos
            
        except Exception as e:
            print(f"Error getting channel videos: {e}")
            return []
    
    def _extract_channel_id(self, url: str) -> str:
        """Extract channel ID from YouTube channel URL"""
        try:
            parsed = urlparse(url)
            
            # youtube.com/channel/CHANNEL_ID
            if '/channel/' in parsed.path:
                return parsed.path.split('/channel/')[1].split('/')[0]
            
            # youtube.com/@username - need to resolve to channel ID
            elif '/@' in parsed.path:
                username = parsed.path.split('/@')[1].split('/')[0]
                return self._resolve_username_to_channel_id(username)
            
            # youtube.com/c/username
            elif '/c/' in parsed.path:
                username = parsed.path.split('/c/')[1].split('/')[0]
                return self._resolve_username_to_channel_id(username)
            
            # Already a channel ID
            elif parsed.path.startswith('UC'):
                return url
            
            return None
            
        except Exception as e:
            print(f"Error extracting channel ID: {e}")
            return None
    
    def _resolve_username_to_channel_id(self, username: str) -> str:
        """Resolve @username to channel ID"""
        try:
            # Search for channel by username
            response = self.youtube.search().list(
                part='snippet',
                q=username,
                type='channel',
                maxResults=1
            ).execute()
            
            if response['items']:
                return response['items'][0]['snippet']['channelId']
            
            return None
            
        except Exception as e:
            print(f"Error resolving username: {e}")
            return None
    
    def comment_on_videos(self, video_ids: List[str], comment_style: str = "helpful",
                          delay_seconds: int = 60, max_comments: int = 10) -> Dict:
        """
        Comment on multiple videos with smart delays
        
        Args:
            video_ids: List of video IDs to comment on
            comment_style: Style of comments
            delay_seconds: Delay between comments (recommend 60-120 seconds)
            max_comments: Max comments in this batch
            
        Returns:
            Results dict
        """
        return self.comment_bot.comment_on_multiple(
            video_ids=video_ids,
            comment_style=comment_style,
            delay_seconds=delay_seconds,
            max_comments=max_comments
        )
