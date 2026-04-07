#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.video_sync_manager import VideoSyncManager
from automation.google_auth import GoogleAuthHelper

def main():
    print("RealE Tube - Drive Sync")
    print("=" * 50)
    
    try:
        auth = GoogleAuthHelper("config/credentials.json")
        drive = auth.get_drive_service()
        
        sync = VideoSyncManager(drive_service=drive)
        results = sync.sync_database_with_drive()
        
        print(f"\nChecked: {results['checked']}")
        print(f"Found in Drive: {results['found']}")
        print(f"Deleted from Drive: {results['deleted']}")
        
        if results['deleted'] > 0:
            print(f"\nDeleted video IDs: {results['deleted_video_ids']}")
            print("\nThese videos have been marked as 'deleted_from_drive' and will not be reposted.")
        else:
            print("\nAll videos are still in Google Drive!")
            
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure credentials.json and token.pickle are in the correct locations.")

if __name__ == "__main__":
    main()
