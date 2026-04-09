# -*- coding: utf-8 -*-
"""
RealE Tube - Main Automation Engine
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from database.db import DatabaseManager
from automation.google_auth import GoogleAuthHelper
from automation.drive_monitor import DriveMonitor
from automation.keyword_generator import KeywordGenerator
from automation.youtube_research import YouTubeResearcher
from automation.youtube_uploader import YouTubeUploader
from automation.performance_monitor import PerformanceMonitor
from pathlib import Path
import json
import time
import threading

class AutomationEngine:
    def __init__(self, config: dict, log_callback=None):
        """
        Initialize automation engine
        
        Args:
            config: Configuration dictionary from settings
            log_callback: Function to call for logging (optional)
        """
        self.config = config
        self.log = log_callback or print
        self.running = False
        self.thread = None
        
        # Initialize components
        self.db = None
        self.auth_helper = None
        self.drive_monitor = None
        self.keyword_gen = None
        self.youtube_researcher = None
        self.youtube_uploader = None
        self.performance_monitor = None
        self.comment_bot = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all automation components"""
        try:
            # Database
            self.db = DatabaseManager()
            self.log("Database initialized", "SUCCESS")
            
            # Initialize services variable
            youtube_service = None
            drive_service = None
            
            # Google Auth (if credentials available)
            youtube_creds = self.config['api']['youtube_credentials']
            if youtube_creds and Path(youtube_creds).exists():
                self.auth_helper = GoogleAuthHelper(youtube_creds)
                
                # Get authenticated services
                youtube_service = self.auth_helper.get_youtube_service()
                drive_service = self.auth_helper.get_drive_service()
                
                # Initialize modules with authenticated services
                self.drive_monitor = DriveMonitor(drive_service=drive_service)
                self.youtube_researcher = YouTubeResearcher(youtube_service=youtube_service)
                self.youtube_uploader = YouTubeUploader(youtube_service=youtube_service)
                
                self.log("Google services authenticated", "SUCCESS")
            
            # AI Keyword Generator (if API key available)
            claude_key = self.config['api']['ai_api_key']
            if claude_key:
                self.keyword_gen = KeywordGenerator(claude_key)
                self.log("AI keyword generator initialized", "SUCCESS")
            
            # Performance Monitor (if all components ready)
            if self.youtube_researcher and self.youtube_uploader:
                self.performance_monitor = PerformanceMonitor(
                    self.db,
                    self.youtube_researcher,
                    self.youtube_uploader,
                    self.config
                )
                self.log("Performance monitor initialized", "SUCCESS")
            
            # Comment Bot (if YouTube service and AI available)
            if youtube_service and self.keyword_gen:
                from automation.comment_bot import CommentBot
                self.comment_bot = CommentBot(youtube_service, self.keyword_gen)
                self.log("Comment bot initialized", "SUCCESS")
            
        except Exception as e:
            self.log(f"Error initializing components: {e}", "ERROR")
    
    def start(self):
        """Start automation in background thread"""
        if self.running:
            self.log("Automation already running", "WARNING")
            return
        
        self.running = True
        
        # Run catchup check immediately on startup
        self.log("Running startup catchup check...", "INFO")
        threading.Thread(target=self._startup_catchup, daemon=True).start()
        
        # Start main automation loop
        self.thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.thread.start()
        self.log("Automation started", "SUCCESS")
    
    def _startup_catchup(self):
        """
        Check for videos that should have been processed while PC was off.
        Runs once on startup to catch up on missed checks.
        """
        try:
            self.log("Checking for videos that need processing...", "INFO")
            
            # Check for any videos that passed their check time while offline
            if self.performance_monitor:
                summary = self.performance_monitor.check_all_videos()
                
                if summary['checked'] > 0:
                    self.log(
                        f"Startup catchup: Processed {summary['checked']} videos that needed attention",
                        "SUCCESS"
                    )
            
            # Process any pending retries
            retry_videos = self.db.get_videos_by_status('retry')
            if retry_videos:
                self.log(f"Found {len(retry_videos)} videos pending retry", "INFO")
            
        except Exception as e:
            self.log(f"Error during startup catchup: {e}", "ERROR")
    
    def stop(self):
        """Stop automation"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.log("Automation stopped", "WARNING")
    
    def _automation_loop(self):
        """Main automation loop"""
        check_interval = 300  # Check every 5 minutes
        
        while self.running:
            try:
                # 1. Check for new videos in Drive
                self._process_new_videos()
                
                # 2. Process pending retries
                self._process_retries()
                
                # 3. Monitor existing videos
                self._monitor_performance()
                
                # Wait before next cycle
                time.sleep(check_interval)
                
            except Exception as e:
                self.log(f"Error in automation loop: {e}", "ERROR")
                time.sleep(60)  # Wait a minute before retrying
    
    def _process_new_videos(self):
        """Check Drive for new videos and process them"""
        if not self.drive_monitor:
            self.log("Drive monitor not initialized - check credentials", "WARNING")
            return
        
        folder_id = self.config['monitoring']['drive_folder_id']
        if not folder_id:
            self.log("Google Drive Folder ID not configured", "WARNING")
            return
        
        self.log(f"Checking Drive folder: {folder_id}", "INFO")
        
        # Check for new videos
        new_videos = self.drive_monitor.watch_folder(folder_id)
        
        self.log(f"Found {len(new_videos)} new videos in Drive", "INFO")
        
        for file_id, filename, description in new_videos:
            self.log(f"New video found: {filename}", "INFO")
            
            try:
                # Skip if already in database (by Drive file ID)
                if self.db.has_drive_file(file_id):
                    self.log(f"Skipping already uploaded: {filename}", "INFO")
                    continue

                # Add to database with Drive file ID
                video_id = self.db.add_video(filename, description, drive_file_id=file_id)
                
                # Download video
                download_path = Path("/tmp") / f"reale_tube_{video_id}_{filename}"
                if self.drive_monitor.download_video(file_id, str(download_path)):
                    
                    # Process and upload
                    self._process_and_upload(video_id, str(download_path), description)
                    
                    # Clean up downloaded file
                    download_path.unlink()
                    
                    # Move to backup folder in Drive
                    folder_id = self.config['monitoring']['drive_folder_id']
                    backup_folder_id = self.drive_monitor.get_or_create_backup_folder(folder_id)
                    
                    if backup_folder_id:
                        if self.drive_monitor.move_to_backup(file_id, backup_folder_id):
                            self.log(f"Moved to backup: {filename}", "SUCCESS")
                        else:
                            self.log(f"Failed to move to backup: {filename}", "WARNING")
                
            except Exception as e:
                self.log(f"Error processing video {filename}: {e}", "ERROR")
    
    def _process_retries(self):
        """Process videos marked for retry"""
        retry_videos = self.db.get_videos_by_status('retry')
        
        for video in retry_videos:
            self.log(f"Retrying video: {video['title_used']} (Attempt {video['attempt_number']})", "WARNING")
            
            try:
                # Re-download from Drive if needed
                # For now, skip if file not available
                # In production, you'd store the Drive file ID
                
                # Generate new metadata with different strategy
                self._process_and_upload(
                    video['id'],
                    video['file_path'],
                    video['original_description'],
                    attempt=video['attempt_number']
                )
                
            except Exception as e:
                self.log(f"Error retrying video {video['id']}: {e}", "ERROR")
    
    def _process_and_upload(self, video_id: int, video_path: str, 
                           description: str, attempt: int = 1):
        """
        Process video: generate metadata and upload
        
        Args:
            video_id: Database video ID
            video_path: Path to video file
            description: Original description
            attempt: Retry attempt number
        """
        # Check video duration for YouTube Shorts
        duration = self.drive_monitor.get_video_duration(video_path)
        is_short = duration > 0 and duration <= 60  # YouTube Shorts: max 60 seconds
        
        if is_short:
            self.log(f"Video is {duration:.1f}s - Will upload as YouTube Short", "INFO")
        
        # 1. Generate keywords
        aggressiveness = self.config['keywords']['keyword_aggressiveness']
        keywords = self.keyword_gen.generate_keywords(description, aggressiveness)
        self.log(f"Generated {len(keywords)} keywords", "INFO")
        
        # 2. Research competitors
        min_likes = self.config['keywords']['competitor_min_likes']
        max_results = self.config['keywords']['competitors_to_analyze']
        competitors = self.youtube_researcher.search_competitors(keywords, min_likes, max_results)
        self.log(f"Found {len(competitors)} competitor videos", "INFO")
        
        # 3. Extract competitor data
        competitor_titles = [v['title'] for v in competitors]
        competitor_descriptions = [v['description'] for v in competitors]
        competitor_tags = self.youtube_researcher.extract_tags_from_competitors(competitors)
        
        # 4. Generate optimized metadata
        title = self.keyword_gen.generate_title(description, competitor_titles, attempt)
        
        # Add #shorts to title if video is under 60 seconds
        if is_short and '#shorts' not in title.lower() and '#short' not in title.lower():
            # Add #shorts at the end if there's room (YouTube title limit: 100 chars)
            if len(title) + 8 <= 100:  # " #shorts" = 8 characters
                title = title + " #shorts"
            else:
                # Truncate and add #shorts
                title = title[:92] + " #shorts"
        
        full_description = self.keyword_gen.generate_description(
            description, keywords, competitor_descriptions, attempt
        )
        tags = self.keyword_gen.generate_tags(keywords, competitor_tags)
        
        self.log(f"Generated metadata - Title: {title[:50]}...", "INFO")
        
        # 5. Upload to YouTube
        youtube_video_id = self.youtube_uploader.upload_video(
            video_path=video_path,
            title=title,
            description=full_description,
            tags=tags,
            privacy_status="public"
        )
        
        # 6. Update database
        self.db.update_video_upload(
            video_id=video_id,
            youtube_video_id=youtube_video_id,
            title=title,
            description=full_description,
            tags=tags,
            keywords=keywords
        )
        
        self.log(f"✓ Video uploaded successfully! YouTube ID: {youtube_video_id}", "SUCCESS")
        
        # 7. Comment on competitor videos (if enabled)
        if (self.comment_bot and 
            self.config.get('comment_bot', {}).get('enabled', False) and 
            len(competitors) > 0):
            
            self.log("Posting comments on competitor videos...", "INFO")
            
            # Get settings
            max_comments = self.config['comment_bot'].get('max_comments_per_video', 3)
            delay = self.config['comment_bot'].get('delay_seconds', 30)
            style = self.config['comment_bot'].get('comment_style', 'helpful')
            
            # Get top competitor video IDs
            competitor_ids = [v['video_id'] for v in competitors[:10]]
            
            # Post comments with AI-generated text
            results = self.comment_bot.comment_on_multiple(
                video_ids=competitor_ids,
                comment_style=style,
                delay_seconds=delay,
                max_comments=max_comments
            )
            
            self.log(
                f"Comment bot: {results['success']} posted, "
                f"{results['failed']} failed, {results['skipped']} skipped",
                "INFO"
            )
    
    def _monitor_performance(self):
        """Monitor performance of uploaded videos"""
        if not self.performance_monitor:
            return
        
        summary = self.performance_monitor.check_all_videos()
        
        if summary['checked'] > 0:
            self.log(
                f"Performance check: {summary['checked']} videos checked, "
                f"{summary['successful']} successful, "
                f"{summary['retrying']} retrying, "
                f"{summary['abandoned']} abandoned",
                "INFO"
            )
    
    def process_single_video(self, video_path: str, description: str):
        """
        Process a single video immediately (for testing)
        
        Args:
            video_path: Path to video file
            description: Video description
        """
        video_id = self.db.add_video(video_path, description)
        self._process_and_upload(video_id, video_path, description)
        return video_id
    
    def get_status(self) -> dict:
        """Get current automation status"""
        stats = self.db.get_statistics()
        
        return {
            'running': self.running,
            'total_videos': sum(stats['by_status'].values()),
            'by_status': stats['by_status'],
            'success_rate': stats['success_rate'],
            'avg_attempts': stats['avg_attempts']
        }
