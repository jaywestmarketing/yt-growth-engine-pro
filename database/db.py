# -*- coding: utf-8 -*-
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
                drive_file_id TEXT,
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
        
        # ── Migrations for existing databases ──
        try:
            cursor.execute('ALTER TABLE videos ADD COLUMN drive_file_id TEXT')
        except Exception:
            pass  # column already exists

        # ── Channels table (multi-channel support) ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL UNIQUE,
                channel_name TEXT,
                is_default INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ── Thumbnail A/B testing ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thumbnail_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                variant_label TEXT NOT NULL,
                thumbnail_path TEXT,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                ctr REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 0,
                is_winner INTEGER DEFAULT 0,
                started_at DATETIME,
                ended_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        ''')

        # ── Scheduled uploads queue ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                description TEXT,
                scheduled_at DATETIME NOT NULL,
                channel_id TEXT,
                is_short INTEGER DEFAULT 0,
                status TEXT DEFAULT 'queued',
                video_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        ''')

        # ── Competitor channels tracking ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL UNIQUE,
                channel_name TEXT,
                subscriber_count INTEGER DEFAULT 0,
                video_count INTEGER DEFAULT 0,
                last_video_date DATETIME,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ── Competitor video snapshots ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_channel_id INTEGER NOT NULL,
                youtube_video_id TEXT NOT NULL,
                title TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                published_at DATETIME,
                tags TEXT,
                snapshot_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_channel_id) REFERENCES competitor_channels(id)
            )
        ''')

        # ── Content plans (AI planner) ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                niche TEXT,
                outline TEXT,
                keywords TEXT,
                target_date DATE,
                status TEXT DEFAULT 'idea',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ── Notifications / alerts ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ── SEO audit log ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seo_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                title_score REAL DEFAULT 0,
                desc_score REAL DEFAULT 0,
                tags_score REAL DEFAULT 0,
                overall_score REAL DEFAULT 0,
                recommendations TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        ''')

        # ── Lifecycle reoptimization history ───────────────────────
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reopt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                old_title TEXT,
                new_title TEXT,
                old_ctr REAL DEFAULT 0,
                old_engagement REAL DEFAULT 0,
                improvement_reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_video(self, file_path: str, description: str, drive_file_id: str = None) -> int:
        """Add new video to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO videos (file_path, original_description, drive_file_id, status)
            VALUES (?, ?, ?, 'pending')
        ''', (file_path, description, drive_file_id))
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()
        return video_id

    def has_drive_file(self, drive_file_id: str) -> bool:
        """Check if a Drive file ID already exists in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(id) FROM videos WHERE drive_file_id = ?', (drive_file_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
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
            WHERE video_count >= 1
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

        try:
            # Total videos by status
            cursor.execute('SELECT status, COUNT(id) as cnt FROM videos GROUP BY status')
            stats['by_status'] = {}
            for row in cursor.fetchall():
                stats['by_status'][row['status']] = row['cnt']

            # Success rate — use simple separate counts
            cursor.execute('SELECT COUNT(id) FROM videos WHERE status IN ("success", "abandoned", "retry")')
            total_processed = cursor.fetchone()[0] or 0

            cursor.execute('SELECT COUNT(id) FROM videos WHERE status = "success"')
            success_count = cursor.fetchone()[0] or 0

            stats['success_rate'] = (success_count / total_processed * 100) if total_processed > 0 else 0

            # Average attempts to success
            cursor.execute('SELECT AVG(attempt_number) FROM videos WHERE status = "success"')
            result = cursor.fetchone()[0]
            stats['avg_attempts'] = result if result is not None else 0

        except Exception as e:
            print(f"Error in get_statistics: {e}")
            stats.setdefault('by_status', {})
            stats.setdefault('success_rate', 0)
            stats.setdefault('avg_attempts', 0)

        conn.close()
        return stats
    
    def delete_video(self, video_id: int):
        """Delete a video and its retry history from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM retry_history WHERE video_id = ?', (video_id,))
        cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        conn.commit()
        conn.close()

    def get_video_by_youtube_id(self, youtube_video_id: str) -> Optional[Dict]:
        """Get a video by its YouTube video ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM videos WHERE youtube_video_id = ?', (youtube_video_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # ── Channels ─────────────────────────────────────────────────

    def add_channel(self, channel_id: str, channel_name: str, is_default: int = 0) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('INSERT OR IGNORE INTO channels (channel_id, channel_name, is_default) VALUES (?,?,?)',
                    (channel_id, channel_name, is_default))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_all_channels(self) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM channels ORDER BY is_default DESC, channel_name')
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    def delete_channel(self, channel_id: str):
        conn = self.get_connection()
        conn.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
        conn.commit()
        conn.close()

    # ── Thumbnail tests ───────────────────────────────────────────

    def add_thumbnail_test(self, video_id: int, variant_label: str, thumbnail_path: str) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO thumbnail_tests (video_id, variant_label, thumbnail_path, started_at)
                       VALUES (?,?,?,?)''',
                    (video_id, variant_label, thumbnail_path, datetime.now().isoformat()))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_thumbnail_tests(self, video_id: int) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM thumbnail_tests WHERE video_id = ? ORDER BY created_at', (video_id,))
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    def get_all_thumbnail_tests(self) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT t.*, v.title_used FROM thumbnail_tests t LEFT JOIN videos v ON t.video_id=v.id ORDER BY t.created_at DESC')
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    # ── Scheduled uploads ─────────────────────────────────────────

    def add_scheduled_upload(self, file_path: str, description: str, scheduled_at: str,
                             channel_id: str = None, is_short: int = 0) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO scheduled_uploads (file_path, description, scheduled_at, channel_id, is_short)
                       VALUES (?,?,?,?,?)''',
                    (file_path, description, scheduled_at, channel_id, is_short))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_scheduled_uploads(self, status: str = None) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        if status:
            cur.execute('SELECT * FROM scheduled_uploads WHERE status=? ORDER BY scheduled_at', (status,))
        else:
            cur.execute('SELECT * FROM scheduled_uploads ORDER BY scheduled_at')
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    def update_scheduled_status(self, upload_id: int, status: str, video_id: int = None):
        conn = self.get_connection()
        if video_id:
            conn.execute('UPDATE scheduled_uploads SET status=?, video_id=? WHERE id=?', (status, video_id, upload_id))
        else:
            conn.execute('UPDATE scheduled_uploads SET status=? WHERE id=?', (status, upload_id))
        conn.commit()
        conn.close()

    def delete_scheduled_upload(self, upload_id: int):
        conn = self.get_connection()
        conn.execute('DELETE FROM scheduled_uploads WHERE id=?', (upload_id,))
        conn.commit()
        conn.close()

    # ── Competitor channels ───────────────────────────────────────

    def add_competitor_channel(self, channel_id: str, channel_name: str) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('INSERT OR IGNORE INTO competitor_channels (channel_id, channel_name) VALUES (?,?)',
                    (channel_id, channel_name))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_all_competitor_channels(self) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM competitor_channels ORDER BY channel_name')
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    def delete_competitor_channel(self, channel_id: str):
        conn = self.get_connection()
        conn.execute('DELETE FROM competitor_videos WHERE competitor_channel_id IN (SELECT id FROM competitor_channels WHERE channel_id=?)', (channel_id,))
        conn.execute('DELETE FROM competitor_channels WHERE channel_id=?', (channel_id,))
        conn.commit()
        conn.close()

    def add_competitor_video(self, competitor_channel_id: int, youtube_video_id: str,
                             title: str, views: int, likes: int, comments: int,
                             published_at: str, tags: str) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO competitor_videos
                       (competitor_channel_id, youtube_video_id, title, views, likes, comments, published_at, tags)
                       VALUES (?,?,?,?,?,?,?,?)''',
                    (competitor_channel_id, youtube_video_id, title, views, likes, comments, published_at, tags))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_competitor_videos(self, competitor_channel_id: int, limit: int = 50) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM competitor_videos WHERE competitor_channel_id=? ORDER BY snapshot_date DESC LIMIT ?',
                    (competitor_channel_id, limit))
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    # ── Content plans ─────────────────────────────────────────────

    def add_content_plan(self, title: str, niche: str, outline: str,
                         keywords: str, target_date: str = None, status: str = 'idea') -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO content_plans (title, niche, outline, keywords, target_date, status)
                       VALUES (?,?,?,?,?,?)''',
                    (title, niche, outline, keywords, target_date, status))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_all_content_plans(self) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM content_plans ORDER BY created_at DESC')
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    def update_content_plan_status(self, plan_id: int, status: str):
        conn = self.get_connection()
        conn.execute('UPDATE content_plans SET status=?, updated_at=? WHERE id=?',
                     (status, datetime.now().isoformat(), plan_id))
        conn.commit()
        conn.close()

    def delete_content_plan(self, plan_id: int):
        conn = self.get_connection()
        conn.execute('DELETE FROM content_plans WHERE id=?', (plan_id,))
        conn.commit()
        conn.close()

    # ── Notifications ─────────────────────────────────────────────

    def add_notification(self, ntype: str, title: str, message: str = "") -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO notifications (type, title, message) VALUES (?,?,?)',
                    (ntype, title, message))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_notifications(self, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        if unread_only:
            cur.execute('SELECT * FROM notifications WHERE is_read=0 ORDER BY created_at DESC LIMIT ?', (limit,))
        else:
            cur.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?', (limit,))
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    def mark_notification_read(self, notification_id: int):
        conn = self.get_connection()
        conn.execute('UPDATE notifications SET is_read=1 WHERE id=?', (notification_id,))
        conn.commit()
        conn.close()

    def clear_notifications(self):
        conn = self.get_connection()
        conn.execute('DELETE FROM notifications')
        conn.commit()
        conn.close()

    # ── SEO audits ────────────────────────────────────────────────

    def add_seo_audit(self, video_id: int, title_score: float, desc_score: float,
                      tags_score: float, overall_score: float, recommendations: str) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO seo_audits (video_id, title_score, desc_score, tags_score, overall_score, recommendations)
                       VALUES (?,?,?,?,?,?)''',
                    (video_id, title_score, desc_score, tags_score, overall_score, recommendations))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_seo_audits(self, video_id: int = None) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        if video_id:
            cur.execute('SELECT * FROM seo_audits WHERE video_id=? ORDER BY created_at DESC', (video_id,))
        else:
            cur.execute('SELECT a.*, v.title_used FROM seo_audits a LEFT JOIN videos v ON a.video_id=v.id ORDER BY a.created_at DESC')
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    # ── Reoptimization tracking ──────────────────────────────────────

    def add_reopt_record(self, video_id: int, old_title: str, new_title: str,
                        old_ctr: float, old_engagement: float, reason: str = None) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO reopt_history
                       (video_id, old_title, new_title, old_ctr, old_engagement, improvement_reason)
                       VALUES (?,?,?,?,?,?)''',
                    (video_id, old_title, new_title, old_ctr, old_engagement, reason))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid

    def get_reopt_history(self, video_id: int = None) -> List[Dict]:
        conn = self.get_connection()
        cur = conn.cursor()
        if video_id:
            cur.execute('SELECT * FROM reopt_history WHERE video_id=? ORDER BY timestamp DESC', (video_id,))
        else:
            cur.execute('SELECT * FROM reopt_history ORDER BY timestamp DESC')
        result = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    def close(self):
        """Close database connection - no-op now since we use per-call connections"""
        pass
