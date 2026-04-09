# -*- coding: utf-8 -*-
"""
RealE Tube - Google Drive Monitor
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from automation.google_auth import GoogleAuthHelper
from googleapiclient.http import MediaIoBaseDownload
import io
import os
from pathlib import Path
from typing import List, Dict, Tuple
import time

class DriveMonitor:
    def __init__(self, credentials_path: str = None, drive_service = None):
        """
        Initialize Google Drive monitor
        
        Args:
            credentials_path: Path to OAuth credentials JSON (optional if drive_service provided)
            drive_service: Pre-authenticated Drive service (optional)
        """
        if drive_service:
            self.drive = drive_service
        elif credentials_path:
            auth_helper = GoogleAuthHelper(credentials_path)
            self.drive = auth_helper.get_drive_service()
        else:
            raise ValueError("Must provide either credentials_path or drive_service")
        
        self.processed_files = set()  # Track already processed files (in-memory)
        self._load_processed_from_db()

    def _load_processed_from_db(self):
        """Load already-uploaded Drive file paths from the database so we
        never re-process a video that was uploaded in a previous session."""
        try:
            from database.db import DatabaseManager
            db = DatabaseManager()
            videos = db.get_all_videos()
            for v in videos:
                fp = v.get('file_path', '')
                if fp:
                    # file_path stores the Drive file ID
                    self.processed_files.add(fp)
        except Exception as e:
            print(f"Warning: could not load processed files from DB: {e}")

    def watch_folder(self, folder_id: str) -> List[Tuple[str, str]]:
        """
        Check folder for new videos

        Args:
            folder_id: Google Drive folder ID to monitor

        Returns:
            List of tuples: (video_file_id, file_name, description_text)
        """
        new_videos = []

        try:
            # Query for video files in folder
            query = f"'{folder_id}' in parents and (mimeType contains 'video/' or name contains '.mp4' or name contains '.mov' or name contains '.avi') and trashed=false"

            results = self.drive.files().list(
                q=query,
                fields="files(id, name, mimeType, createdTime)",
                orderBy="createdTime desc"
            ).execute()

            files = results.get('files', [])

            for file in files:
                file_id = file['id']
                file_name = file['name']

                # Skip if already processed (in-memory or from DB)
                if file_id in self.processed_files:
                    continue

                # Use the filename (without extension) as the description
                base_name = Path(file_name).stem
                # Clean up the filename: replace underscores/hyphens with spaces
                description = base_name.replace('_', ' ').replace('-', ' ')

                new_videos.append((file_id, file_name, description))
                self.processed_files.add(file_id)
                print(f"Found video: {file_name} - Using description: {description}")

            return new_videos

        except Exception as e:
            print(f"Error watching folder: {e}")
            return []
    
    def _find_description(self, folder_id: str, video_filename: str) -> str:
        """
        Find description file matching video filename
        
        Looks for:
        - videoname_description.txt
        - videoname.txt
        - description.txt
        """
        # Get base name without extension
        base_name = Path(video_filename).stem
        
        # Try different naming patterns
        patterns = [
            f"{base_name}_description.txt",
            f"{base_name}.txt",
            "description.txt"
        ]
        
        try:
            for pattern in patterns:
                # Escape single quotes for API query by doubling them
                escaped_pattern = pattern.replace("'", "''")
                
                query = f"'{folder_id}' in parents and name='{escaped_pattern}' and trashed=false"
                
                results = self.drive.files().list(
                    q=query,
                    fields="files(id, name)"
                ).execute()
                
                files = results.get('files', [])
                
                if files:
                    # Read the description file
                    file_id = files[0]['id']
                    return self._read_text_file(file_id)
            
            return None
            
        except Exception as e:
            print(f"Error finding description: {e}")
            return None
    
    def _find_generic_description(self, folder_id: str) -> str:
        """Find a generic description.txt in folder"""
        try:
            query = f"'{folder_id}' in parents and name='description.txt' and trashed=false"
            
            results = self.drive.files().list(
                q=query,
                fields="files(id)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return self._read_text_file(files[0]['id'])
            
            return None
            
        except Exception as e:
            print(f"Error finding generic description: {e}")
            return None
    
    def _read_text_file(self, file_id: str) -> str:
        """Read text content from a Drive file"""
        try:
            request = self.drive.files().get_media(fileId=file_id)
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            content = fh.getvalue().decode('utf-8')
            return content.strip()
            
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def download_video(self, file_id: str, destination_path: str) -> bool:
        """
        Download video file from Drive
        
        Args:
            file_id: Google Drive file ID
            destination_path: Where to save the file
            
        Returns:
            True if successful
        """
        try:
            request = self.drive.files().get_media(fileId=file_id)
            
            # Ensure directory exists
            Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"Download progress: {int(status.progress() * 100)}%")
            
            print(f"Video downloaded to: {destination_path}")
            return True
            
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False
    
    def get_file_info(self, file_id: str) -> Dict:
        """Get file metadata"""
        try:
            file = self.drive.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime"
            ).execute()
            
            return file
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def get_video_duration(self, file_path: str) -> float:
        """
        Get video duration in seconds
        
        Args:
            file_path: Path to video file
            
        Returns:
            Duration in seconds, or 0 if unable to determine
        """
        try:
            # Try using moviepy (most reliable, pure Python)
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(file_path)
            duration = video.duration
            video.close()
            
            return duration
            
        except ImportError:
            print("moviepy not installed, trying opencv...")
            return self._get_duration_opencv(file_path)
        except Exception as e:
            print(f"moviepy error: {e}, trying opencv...")
            return self._get_duration_opencv(file_path)
    
    def _get_duration_opencv(self, file_path: str) -> float:
        """Get duration using opencv as fallback"""
        try:
            import cv2
            
            video = cv2.VideoCapture(file_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            video.release()
            
            return duration
            
        except ImportError:
            print("opencv not installed, using file size estimate...")
            return self._get_duration_estimate(file_path)
        except Exception as e:
            print(f"opencv error: {e}, using estimate...")
            return self._get_duration_estimate(file_path)
    
    def _get_duration_estimate(self, file_path: str) -> float:
        """Rough estimate based on file size"""
        try:
            import os
            # Very rough estimate: assume 1MB per 5 seconds for typical video
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            estimated_duration = file_size_mb * 5
            print(f"Using file size estimate: {estimated_duration:.1f}s (may be inaccurate)")
            return estimated_duration
        except:
            return 0
    
    def mark_as_processed(self, file_id: str):
        """Mark a file as processed to avoid reprocessing"""
        self.processed_files.add(file_id)
    
    def reset_processed_files(self):
        """Clear the processed files cache"""
        self.processed_files.clear()
    
    def move_to_backup(self, file_id: str, backup_folder_id: str) -> bool:
        """
        Move a file to backup folder after processing
        
        Args:
            file_id: Google Drive file ID to move
            backup_folder_id: Destination backup folder ID
            
        Returns:
            True if successful
        """
        try:
            # Get current file info
            file = self.drive.files().get(
                fileId=file_id,
                fields='parents, name'
            ).execute()
            
            file_name = file.get('name')
            previous_parents = ",".join(file.get('parents', []))
            
            # Move file to backup folder
            file = self.drive.files().update(
                fileId=file_id,
                addParents=backup_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            print(f"✓ Moved to backup: {file_name}")
            return True
            
        except Exception as e:
            print(f"Error moving file to backup: {e}")
            return False
    
    def get_or_create_backup_folder(self, parent_folder_id: str, backup_folder_name: str = "RealE-Tube-BackUp") -> str:
        """
        Get backup folder ID, or create it if it doesn't exist
        
        Args:
            parent_folder_id: Parent folder where backup should be
            backup_folder_name: Name of backup folder
            
        Returns:
            Backup folder ID
        """
        try:
            # Search for existing backup folder
            query = f"'{parent_folder_id}' in parents and name='{backup_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = self.drive.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                # Backup folder exists
                return files[0]['id']
            else:
                # Create backup folder
                file_metadata = {
                    'name': backup_folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_folder_id]
                }
                
                folder = self.drive.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                
                print(f"✓ Created backup folder: {backup_folder_name}")
                return folder.get('id')
                
        except Exception as e:
            print(f"Error getting/creating backup folder: {e}")
            return None
