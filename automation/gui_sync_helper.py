"""
RealE Tube - GUI Sync Helper
Provides sync functionality for the GUI
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.video_sync_manager import VideoSyncManager
from automation.google_auth import GoogleAuthHelper
import threading

class GUISyncHelper:
    def __init__(self, callback=None):
        """
        Initialize GUI Sync Helper
        
        Args:
            callback: Function to call with sync results (optional)
        """
        self.callback = callback
        self.sync_running = False
    
    def run_sync(self):
        """Run sync in background thread"""
        if self.sync_running:
            if self.callback:
                self.callback({"error": "Sync already running"})
            return
        
        thread = threading.Thread(target=self._sync_thread, daemon=True)
        thread.start()
    
    def _sync_thread(self):
        """Background sync thread"""
        self.sync_running = True
        
        try:
            # Authenticate with Drive
            auth = GoogleAuthHelper("confi         ials.json")
            drive = auth.get_drive_service()
            
            # Run sync
            sync = VideoSyncManager(drive_service=drive)
            results = sync.sync_database_wi            res        
            # Callback with results
            if sel          :
            if sel          :
sul           sul         cesul           sul         cesul           sul         cesul         sul           "found": results['found'],
                    "deleted": results   eleted'],
                                                          de                            })
        
        except Exception as e:
            if self.callback:
                self.callback({
                    "success": False,
                    "error": str(e)
                })
        
        finally:
            self.sync_running = False
