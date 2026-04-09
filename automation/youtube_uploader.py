# -*- coding: utf-8 -*-
"""
RealE Tube - YouTube Uploader
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from googleapiclient.http import MediaFileUpload
from automation.google_auth import GoogleAuthHelper
from typing import List, Dict
import os

class YouTubeUploader:
    def __init__(self, credentials_path: str = None, youtube_service = None):
        """
        Initialize YouTube uploader
        
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
    
    def upload_video(self, 
                    video_path: str,
                    title: str,
                    description: str,
                    tags: List[str],
                    category_id: str = "22",  # People & Blogs
                    privacy_status: str = "public") -> str:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (22 = People & Blogs, 27 = Education)
            privacy_status: "public", "private", or "unlisted"
            
        Returns:
            YouTube video ID
        """
        
        # Validate file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Prepare request body
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,  # Upload in a single request
            resumable=True,
            mimetype='video/*'
        )
        
        # Execute upload
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response['id']
        print(f"Video uploaded successfully! ID: {video_id}")
        
        return video_id
    
    def update_video_metadata(self, 
                             video_id: str,
                             title: str = None,
                             description: str = None,
                             tags: List[str] = None) -> bool:
        """
        Update metadata for an existing video
        
        Args:
            video_id: YouTube video ID
            title: New title (optional)
            description: New description (optional)
            tags: New tags (optional)
            
        Returns:
            True if successful
        """
        try:
            # Get current video details
            response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not response['items']:
                return False
            
            snippet = response['items'][0]['snippet']
            
            # Update only provided fields
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags
            
            # Update video
            update_response = self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating video: {e}")
            return False
    
    def delete_video(self, video_id: str) -> bool:
        """
        Delete a video from YouTube
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if successful
        """
        try:
            self.youtube.videos().delete(id=video_id).execute()
            print(f"Video {video_id} deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting video: {e}")
            return False
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """
        Set custom thumbnail for video
        
        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(thumbnail_path):
                print(f"Thumbnail not found: {thumbnail_path}")
                return False
            
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            
            print(f"Thumbnail set for video {video_id}")
            return True
            
        except Exception as e:
            print(f"Error setting thumbnail: {e}")
            return False
