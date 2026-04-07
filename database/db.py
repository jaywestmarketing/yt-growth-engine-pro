"""
RealE Tube - Database Manager (Thread-Safe)
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

class DatabaseManager:
    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "reale_tube.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize schema
        self.init_database()
    
    def get_connection(self):
        """Get a new connection for the current thread (thread-safe)"""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                original_description TEXT,
                youtube_video_id TEXT,
                
                -- Attempt tracking
                attempt_number INTEGER DEFAULT 1,
                max_attempts INTEGER DEFAULT 3,
                status TEXT DEFAULT 'uploaded',
                
                -- Metadata used
                title_used TEXT,
                description_used TEXT,
                tags_used TEXT,
                keywords_targeted TEXT,
                
                -- Performance metrics
                views INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                ctr REAL DEFAULT 0.0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                watch_time_minutes REAL DEFAULT 0.0,
                
                -- Timestamps
                upload_date DATETIME,
                last_checked DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Retry history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retry_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                attempt_number INTEGER NOT NULL,
                youtube_video_id TEXT,
                title_used TEXT,
                tags_used TEXT,
                keywords_used TEXT,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        ''')
        
        # Keywords performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                video_count INTEGER DEFAULT 0,
                avg_views REAL DEFAULT 0.0,
                avg_ctr REAL DEFAULT 0.0,
                avg_engagement REAL DEFAULT 0.0,
                success_count INTEGER DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(keyword)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_video(self, file_path: str, description: str) -> int:
        """Add new video to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO videos (file_path, original_description, status)
            VALUES (?, ?, 'pending')
        ''', (file_path, description))
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()
        return video_id
    
    def update_video_upload(self, video_id: int, youtube_video_id: str, 
                           title: str, description: str, tags: List[str], 
                           keywords: List[str]):
        """Update video with upload information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE videos 
            SET youtube_video_id = ?,
                title_used = ?,
                description_used = ?,
                tags_used = ?,
                keywords_targeted = ?,
                status = 'uploaded',
                upload_date = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            youtube_video_id,
            title,
            description,
            json.dumps(tags),
            json.dumps(keywords),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            video_id
        ))
        conn.commit()
        conn.close()
    
    def update_video_metrics(self, video_id: int, metrics: Dict):
        """Update video performance metrics"""
        views = metrics.get('views', 0)
        likes = metrics.get('likes', 0)
        comments = metrics.get('comments', 0)
        impressions = metrics.get('impressions', 1)
        
        # Calculate derived metrics
        ctr = (views / impressions * 100) if impressions > 0 else 0
        engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE videos 
            SET views = ?,
                impressions = ?,
                ctr = ?,
                likes = ?,
                comments = ?,
                engagement_rate = ?,
                last_checked = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            views,
            impressions,
            ctr,
            likes,
            comments,
            engagement_rate,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            video_id
        ))
        conn.commit()
        conn.close()
    
    def mark_for_retry(self, video_id: int, reason: str):
        """Mark video for retry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current attempt info
        cursor.execute('SELECT attempt_number, youtube_video_id, title_used, tags_used, keywords_targeted FROM videos WHERE id = ?', (video_id,))
        row = cursor.fetchone()
        
        if row:
            # Log retry history
            cursor.execute('''
                INSERT INTO retry_history (video_id, attempt_number, youtube_video_id, title_used, tags_used, keywords_used, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (video_id, row[0], row[1], row[2], row[3], row[4], reason))
            
            # Update video status
            new_attempt = row[0] + 1
            cursor.execute('''
                UPDATE videos 
                SET status = 'retry',
                    attempt_number = ?,
                    youtube_video_id = NULL,
                    updated_at = ?
                WHERE id = ?
            ''', (new_attempt, datetime.now().isoformat(), video_id))
            
            conn.commit()
        conn.close()
    
    def mark_as_abandoned(self, video_id: int):
        """Mark video as abandoned after max retries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE videos 
            SET status = 'abandoned',
                updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), video_id))
        conn.commit()
        conn.close()
    
    def mark_as_success(self, video_id: int):
        """Mark video as successful"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE videos 
            SET status = 'success',
                updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), video_id))
        conn.commit()
        conn.close()
    
    def get_videos_by_status(self, status: str) -> List[Dict]:
        """Get all videos with specific status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM videos WHERE status = ? ORDER BY created_at DESC', (status,))
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def get_all_videos(self) -> List[Dict]:
        """Get all videos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM videos ORDER BY created_at DESC')
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def get_video(self, video_id: int) -> Optional[Dict]:
        """Get specific video by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_videos_for_monitoring(self) -> List[Dict]:
        """Get videos that need performance monitoring"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM videos 
            WHERE status IN ('uploaded', 'monitoring')
            AND youtube_video_id IS NOT NULL
            ORDER BY upload_date DESC
        ''')
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def update_keyword_performance(self, keyword: str, video_success: bool, metrics: Dict):
        """Update keyword performance tracking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute('SELECT * FROM keyword_performance WHERE keyword = ?', (keyword,))
        row = cursor.fetchone()
        
        if row:
            # Update existing
            video_count = row['video_count'] + 1
            success_count = row['success_count'] + (1 if video_success else 0)
            
            # Running average
            avg_views = (row['avg_views'] * row['video_count'] + metrics.get('views', 0)) / video_count
            avg_ctr = (row['avg_ctr'] * row['video_count'] + metrics.get('ctr', 0)) / video_count
            avg_engagement = (row['avg_engagement'] * row['video_count'] + metrics.get('engagement_rate', 0)) / video_count
            
            cursor.execute('''
                UPDATE keyword_performance 
                SET video_count = ?,
                    avg_views = ?,
                    avg_ctr = ?,
                    avg_engagement = ?,
                    success_count = ?,
                    updated_at = ?
                WHERE keyword = ?
            ''', (video_count, avg_views, avg_ctr, avg_engagement, success_count, datetime.now().isoformat(), keyword))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO keyword_performance (keyword, video_count, avg_views, avg_ctr, avg_engagement, success_count)
                VALUES (?, 1, ?, ?, ?, ?)
            ''', (keyword, metrics.get('views', 0), metrics.get('ctr', 0), metrics.get('engagement_rate', 0), 1 if video_success else 0))
        
        conn.commit()
        conn.close()
    
    def get_top_keywords(self, limit: int = 10) -> List[Dict]:
        """Get top performing keywords"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM keyword_performance 
            WHERE video_count >= 3
            ORDER BY avg_views DESC, avg_engagement DESC
            LIMIT ?
        ''', (limit,))
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total videos by status
        cursor.execute('SELECT status, COUNT(*) as count FROM videos GROUP BY status')
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Success rate
        cursor.execute('SELECT COUNT(*) as total FROM videos WHERE status IN ("success", "abandoned", "retry")')
        total_processed = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as success FROM videos WHERE status = "success"')
        success_count = cursor.fetchone()['success']
        
        stats['success_rate'] = (success_count / total_processed * 100) if total_processed > 0 else 0
        
        # Average attempts to success
        cursor.execute('SELECT AVG(attempt_number) as avg_attempts FROM videos WHERE status = "success"')
        stats['avg_attempts'] = cursor.fetchone()['avg_attempts'] or 0
        
        conn.close()
        return stats
    
    def close(self):
        """Close database connection - no-op now since we use per-call connections"""
        pass
