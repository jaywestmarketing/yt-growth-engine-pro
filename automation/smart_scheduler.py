# -*- coding: utf-8 -*-
"""
RealE Tube - Smart Scheduler
Automatically schedules video uploads for optimal posting times
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from database.db import DatabaseManager
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz


class SmartScheduler:
    """
    Intelligently schedule video uploads based on:
    - Upload history analysis (your own peak times)
    - Competitor posting patterns
    - Day-of-week trends
    - Time-of-day trends
    """

    def __init__(self, timezone: str = 'UTC'):
        """
        Initialize smart scheduler

        Args:
            timezone: User's timezone (e.g. 'America/New_York')
        """
        self.db = DatabaseManager()
        self.tz = pytz.timezone(timezone)

    def find_optimal_times(self) -> Dict:
        """
        Analyze upload history to find best posting times

        Returns:
            Dict with optimal hours, days, and scores
        """
        try:
            videos = self.db.get_all_videos()
        except Exception:
            return {'hours': {}, 'days': {}, 'best_time': None}

        hour_stats = {}  # hour -> {count, avg_views}
        day_stats = {}   # day_name -> {count, avg_views}

        for v in videos:
            date_str = v.get('upload_date') or v.get('created_at') or ''
            views = v.get('views') or 0

            if not date_str:
                continue

            try:
                dt = self._parse_date(date_str)
                if not dt:
                    continue

                h = dt.hour
                d = dt.strftime('%A')

                hour_stats.setdefault(h, {'count': 0, 'views': 0})
                hour_stats[h]['count'] += 1
                hour_stats[h]['views'] += views

                day_stats.setdefault(d, {'count': 0, 'views': 0})
                day_stats[d]['count'] += 1
                day_stats[d]['views'] += views

            except Exception:
                continue

        # Find top hours
        best_hours = {}
        if hour_stats:
            for h, s in hour_stats.items():
                avg = s['views'] / max(s['count'], 1)
                best_hours[h] = avg

        # Find top days
        best_days = {}
        if day_stats:
            for d, s in day_stats.items():
                avg = s['views'] / max(s['count'], 1)
                best_days[d] = avg

        # Get single best time
        best_time = None
        if best_hours:
            best_hour = max(best_hours.items(), key=lambda x: x[1])[0]
            if best_days:
                best_day = max(best_days.items(), key=lambda x: x[1])[0]
                best_time = (best_day, best_hour)

        return {
            'hours': best_hours,
            'days': best_days,
            'best_time': best_time,
            'total_videos_analyzed': len(videos)
        }

    def suggest_schedule(self, num_suggestions: int = 5) -> List[Tuple[str, str]]:
        """
        Generate schedule suggestions for upcoming uploads

        Args:
            num_suggestions: How many time slots to suggest

        Returns:
            List of (datetime_str, reason) tuples
        """
        optimal = self.find_optimal_times()

        suggestions = []
        if not optimal['best_time']:
            # Fallback to general best practices
            suggestions.extend([
                (self._next_weekday_at_time('Monday', 12), "Weekday morning (general best practice)"),
                (self._next_weekday_at_time('Wednesday', 15), "Mid-week afternoon"),
                (self._next_weekday_at_time('Friday', 18), "Friday evening"),
                (self._next_weekday_at_time('Saturday', 10), "Weekend morning"),
                (self._next_weekday_at_time('Sunday', 14), "Sunday afternoon"),
            ])
        else:
            best_day, best_hour = optimal['best_time']

            # Primary slot: best performing time
            primary = self._next_weekday_at_time(best_day, best_hour)
            suggestions.append((primary, f"Your best time ({best_day} {best_hour:02d}:00)"))

            # Secondary slots: alternative high-performing times
            if len(optimal['hours']) > 1:
                sorted_hours = sorted(optimal['hours'].items(), key=lambda x: x[1], reverse=True)
                for idx, (h, score) in enumerate(sorted_hours[1:num_suggestions]):
                    day = best_day if idx == 0 else self._next_other_day(best_day, idx)
                    slot = self._next_weekday_at_time(day, h)
                    suggestions.append((slot, f"Alternative time ({day} {h:02d}:00)"))

        return suggestions[:num_suggestions]

    def schedule_batch(self, video_files: List[str], descriptions: List[str],
                       spacing_hours: int = 24) -> List[Dict]:
        """
        Schedule multiple videos with optimal spacing

        Args:
            video_files: List of video file paths
            descriptions: List of video descriptions
            spacing_hours: Hours between each upload

        Returns:
            List of scheduled upload dicts
        """
        suggestions = self.suggest_schedule(len(video_files))
        scheduled = []

        for idx, (video_path, description) in enumerate(zip(video_files, descriptions)):
            if idx < len(suggestions):
                schedule_time, reason = suggestions[idx]
            else:
                # Add spacing if more videos than suggestions
                prev_time = datetime.fromisoformat(suggestions[-1][0])
                schedule_time = (prev_time + timedelta(hours=spacing_hours)).isoformat()
                reason = f"Auto-spaced ({spacing_hours}h after previous)"

            # Add to database
            upload_id = self.db.add_scheduled_upload(
                file_path=video_path,
                description=description,
                scheduled_at=schedule_time,
                is_short=0  # Can be enhanced to detect shorts
            )

            scheduled.append({
                'upload_id': upload_id,
                'file': video_path,
                'scheduled_at': schedule_time,
                'reason': reason
            })

        return scheduled

    def get_upcoming_uploads(self, hours_ahead: int = 168) -> List[Dict]:
        """
        Get uploads scheduled for the next N hours

        Args:
            hours_ahead: Hours to look ahead (default 7 days)

        Returns:
            List of scheduled uploads
        """
        try:
            upcoming = self.db.get_scheduled_uploads(status='queued')
        except Exception:
            return []

        now = datetime.now(self.tz)
        cutoff = now + timedelta(hours=hours_ahead)

        filtered = []
        for upload in upcoming:
            scheduled = self._parse_date(upload.get('scheduled_at'))
            if scheduled and now <= scheduled <= cutoff:
                filtered.append(upload)

        # Sort by scheduled time
        filtered.sort(key=lambda x: x.get('scheduled_at', ''))
        return filtered

    def recommend_schedule_adjustment(self, video_performance: Dict) -> Optional[str]:
        """
        Suggest if a video should be re-uploaded at a better time

        Args:
            video_performance: Video metrics dict

        Returns:
            Reason to reschedule, or None if timing was good
        """
        ctr = video_performance.get('ctr', 0)
        views = video_performance.get('views', 0)
        upload_time = video_performance.get('upload_date')

        if not upload_time or views < 100:
            return None

        optimal = self.find_optimal_times()
        if not optimal['best_time']:
            return None

        best_day, best_hour = optimal['best_time']
        upload_dt = self._parse_date(upload_time)

        if not upload_dt:
            return None

        upload_hour = upload_dt.hour
        upload_day = upload_dt.strftime('%A')

        # Check if uploaded at suboptimal time
        if upload_hour != best_hour or upload_day != best_day:
            if ctr < 3.0:
                return (f"Video uploaded at {upload_day} {upload_hour:02d}:00 (suboptimal). "
                       f"Best time is {best_day} {best_hour:02d}:00. "
                       f"Consider reuploading or promoting at optimal time.")

        return None

    # ── Helper methods ────────────────────────────────────────────

    def _next_weekday_at_time(self, day_name: str, hour: int) -> str:
        """
        Get next occurrence of a weekday at a specific hour

        Args:
            day_name: Day name (Monday, Tuesday, etc.)
            hour: Hour (0-23)

        Returns:
            ISO datetime string
        """
        day_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        target_day = day_map.get(day_name, 0)
        now = datetime.now(self.tz)
        current_day = now.weekday()

        # Days until target
        days_ahead = target_day - current_day
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7

        target_date = now + timedelta(days=days_ahead)
        target_dt = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)

        return target_dt.isoformat()

    def _next_other_day(self, primary_day: str, offset: int) -> str:
        """Get another day offset from primary"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        idx = days.index(primary_day)
        return days[(idx + offset) % 7]

    @staticmethod
    def _parse_date(value):
        """Parse ISO date string"""
        if not value:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        return None
