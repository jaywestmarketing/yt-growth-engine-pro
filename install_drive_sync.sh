#!/bin/bash

# RealE Tube - Drive Sync Installation
# Simple, error-free installation script

echo "========================================="
echo "RealE Tube - Drive Sync Installation"
echo "========================================="
echo ""

# Check we're in the right directory
if [ ! -d "automation" ] || [ ! -d "database" ]; then
    echo "Error: Must run from reale-tube directory"
    exit 1
fi

echo "[1/4] Updating database schema..."
python3 << 'PYTHONEOF'
import sqlite3
from pathlib import Path

db_path = Path("data/reale_tube.db")
db_path.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(videos)")
columns = [col[1] for col in cursor.fetchall()]

if 'drive_file_id' not in columns:
    cursor.execute('ALTER TABLE videos ADD COLUMN drive_file_id TEXT')
    print("  ✓ Added drive_file_id column")
else:
    print("  ✓ Database already up to date")

conn.commit()
conn.close()
PYTHONEOF

echo ""
echo "[2/4] Creating viecho "[2/4] Creating viecho "[2/4] Crtion/video_sync_manager.py << 'PYEOF'
"""
RealE Tube - Video Sync Manager
Copyright © 2024 RCopyright © 2024 RCopyright © 2024 RCopyrved.
"""

from typing import List, Dict, Optional
from datefrom datefrom datefrom datefrom datmport Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import DatabaseManager
from afrom afrom afrom afrom afrom afrom afroHelper

class VideoSyncManager:
    def __init__(self, db_manager:    def __init__(self, db_manager: ic    def __init__(self, db_manager:nager or DatabaseManager()
        self.drive = drive_service
                         xists_in_drive(self, file_id: str) -> bool:
        if not self.drive:
            return True
            return True
e:
sts_inve.files().get(fileId=file_id, fields='id').execute()
            return True
        except:
            return False
    
    def extract_drive_id_from_path(self, file_path: str) -> Opt    def ext
         ath_parts = Path(file_path).parts
        for part in path_parts:
            if 25 <= len(part) <= 45 and all(c.isalnum() or c in '-_' for c in             if 25 <= len(part) <= 45 and all(c.isalnum() or c in ef  ync_database_with_drive(self) -> Dict:
        if not self.drive:
            return {'error': 'Dr         ce not initialized', 'checked': 0, 'found': 0, 'deleted':             return {'error': 'Dr      self.db.get_videos_by_status('uploaded')
        uploaded_videos.extend(self.db        uploaded_videos.extend(self.db        uploaded_videos.extend(self.db        uploaded_videos.extend(self.db        uploadedked = 0
        found = 0
        deleted = 0
        deleted_ids = []
        
        for video in uploa        for video in uploid        for video in u          for video  video.get('drive_file_id') or self.extract_drive_id_from_path(video[        for video in u    
            if drive_id:
                ch                ch                ch                ch                ch                   ch                ch         else:
                    deleted += 1
                    deleted_ids.append(video_id)
                    self._mark_video_deleted(video_id)
        
        return {'checked': checked, 'found': found, 'deleted': deleted, 'deleted_video_ids': deleted_ids}
    
    def _mark_video_deleted(self, video_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE videos         cursor.execute("UPDATE videos         cursor.execute("UPDATE videos         cursor.execute("UPDATE videos         cursor.execute("UPDATE videos         cursor.exec    
    def get_active    def get_active(s    def get_active    d     conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM videos 
            WHERE status NOT IN ('deleted_from_drive', 'abandoned')
            AND youtube_video_id IS NOT NULL
            ORDER BY upload_date DESC
        """)
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
PYEOF

echo "  ✓ Created video_sync_manager.py"

echo ""
echo ""
✓ Created video_sync_manager.py"
or.fetchaln/or.fetci.py << 'PYEOF'
#!/usr/bin/env python3
"""RealE Tube - Drive Sync CLI"""
import sys
from pathlib import Pathfros.from pathlib import Pathfros.from pathlib import)
from pathlib import Pathfros.from pathport VideoSyncManager
from automation.google_auth import GoogleAuthHelper

def main():
    print("RealE Tube - Drive Sync")
    print("=" * 50)
    
    creds_path = "config/credentials.json"
    auth = GoogleAuthHelper(creds_path)
    drive = auth.get_drive_service()
    
    sync = VideoSyncManager(drive_service=drive)
    results = sync.syn    results = sync.syn    res    print(f"Checked: {results['checked']}")
    print(f"Found i    print(f"Found i    print(f"Found i    print(f"Found i    printed    print(f"Found i    print(f"Found i    p       print(f"Deleted video IDs: {results['deleted_video_ids']}")

if __name__ == "__main__":
    main()
PYEOFPYEOFPYEOFPYEOFPYEOonPYEOFPYEOFPy
echo "  ✓ Created sync_cli.py"

echo ""
echo "[4/4] Creatiecho "umecho "on..."

cat > DRIVE_SYNC_GUIDE.md << 'MDEOF'
# Drive Sync - Quick Guide

## Run Sync Check
```b```b```b```b```b```b```b```b```bpy```b```b`Integration
Add to your automation_engine.py:
```python
from automation.video_sync_manager import VideoSyncManager

sync_manager = VideoSyncMsync_manager = VideoSyncMsync_manager = VideoSyncM_database_with_drive()
safe_videos = sync_manager.get_active_videos_for_safossafe_videos = sync_manager.get_active_vidave status: 'deleted_from_drive'
MDEOF

echo "  ✓ Created DRIVE_SYNC_GUIDE.mdechececho "  ✓ Created DRIVE_SYNC_GUIDE.mdechecech======"
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Test it:"
echo "  python3 automation/sync_cli.py"
echo ""
echo "Read guide:"
echo "  cat DRIVE_SYNC_GUIDE.md"
echo ""
