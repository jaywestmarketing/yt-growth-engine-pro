# -*- coding: utf-8 -*-
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db import DatabaseManager

class VideoSyncManager:
    def __init__(self, db_manager=None, drive_service=None):
        self.db = db_manager or DatabaseManager()
        self.drive = drive_service
    
    def check_file_exists_in_drive(self, file_id: str) -> bool:
        if not self.drive:
            return True
        try:
            self.drive.files().get(fileId=file_id, fields='id').execute()
            return True
        except:
            return False
    
    def extract_drive_id_from_path(self, file_path: str) -> Optional[str]:
        path_parts = Path(file_path).parts
        for part in path_parts:
            if 25 <= len(part) <= 45 and all(c.isalnum() or c in '-_' for c in part):
                return part
        return None
    
    def sync_database_with_drive(self) -> Dict:
        if not self.drive:
            return {'error': 'No drive', 'checked': 0, 'found': 0, 'deleted': 0}
        videos = self.db.get_videos_by_status('uploaded')
        videos.extend(self.db.get_videos_by_status('monitoring'))
        videos.extend(self.db.get_videos_by_status('success'))
        checked = found = deleted = 0
        deleted_ids = []
        for video in videos:
            video_id = video['id']
            drive_id = video.get('drive_file_id') or self.extract_drive_id_from_path(video['file_path'])
            if drive_id:
                checked += 1
                if self.check_file_exists_in_drive(drive_id):
                    found += 1
                else:
                    deleted += 1
                    deleted_ids.append(video_id)
                    self._mark_video_deleted(video_id)
        return {'checked': checked, 'found': found, 'deleted': deleted, 'deleted_video_ids': deleted_ids}
    
    def _mark_video_deleted(self, video_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE videos SET status = ?, updated_at = ? WHERE id = ?", ('deleted_from_drive', datetime.now().isoformat(), video_id))
        conn.commit()
        conn.close()
    
    def get_active_videos_for_repost(self) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos WHERE status NOT IN ('deleted_from_drive', 'abandoned') AND youtube_video_id IS NOT NULL ORDER BY upload_date DESC")
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
