# -*- coding: utf-8 -*-
"""
RealE Tube - Central YouTube API Quota Manager

Singleton that tracks YouTube Data API v3 quota usage across ALL modules
(researcher, uploader, comment bot, performance monitor, etc.) so the
entire app knows when to stop hitting the API.

Quota facts:
- Default daily limit: 10,000 units
- Resets at midnight US Pacific Time (07:00 UTC during PST, 08:00 UTC during PDT)
- videos.list = 1 unit
- search.list = 100 units
- videos.insert = 1,600 units  (!!!)
- videos.update = 50 units
- commentThreads.insert = 50 units
- thumbnails.set = 50 units
- channels.list = 1 unit

Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional


# Quota cost per YouTube Data API endpoint (units)
API_COSTS = {
    'videos.list': 1,
    'videos.insert': 1600,
    'videos.update': 50,
    'videos.delete': 50,
    'search.list': 100,
    'commentThreads.list': 1,
    'commentThreads.insert': 50,
    'comments.insert': 50,
    'channels.list': 1,
    'playlists.list': 1,
    'playlistItems.list': 1,
    'thumbnails.set': 50,
    'captions.list': 50,
    'captions.insert': 400,
}


class QuotaManager:
    """
    Thread-safe singleton quota tracker.

    Use get_instance() to access the same manager from any module.
    """

    _instance = None
    _lock = threading.Lock()

    DAILY_LIMIT = 10000
    # Reserve a small buffer so one more action doesn't push us over
    SAFETY_BUFFER = 200
    STATE_FILE = Path(__file__).parent.parent / "data" / "quota_state.json"

    def __init__(self):
        if QuotaManager._instance is not None:
            raise RuntimeError("Use QuotaManager.get_instance() instead")

        self.used_today = 0
        self.exhausted = False
        self.last_reset_day = None  # YYYY-MM-DD string in Pacific Time
        self.exhausted_until = None  # datetime when the next reset happens
        self._log_callback = None

        # Load persisted state (survives app restart)
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._load_state()
        self._check_daily_reset()

    @classmethod
    def get_instance(cls) -> "QuotaManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def set_log_callback(self, callback):
        """Register a log function so this class can report to the UI."""
        self._log_callback = callback

    def _log(self, message: str, level: str = "INFO"):
        if self._log_callback:
            try:
                self._log_callback(message, level)
            except Exception:
                pass
        else:
            print(f"[{level}] QuotaManager: {message}")

    # ── Public API ────────────────────────────────────────────────

    def can_spend(self, endpoint: str) -> bool:
        """Return True if we can still call this endpoint today."""
        self._check_daily_reset()
        if self.exhausted:
            return False

        cost = API_COSTS.get(endpoint, 1)
        return (self.used_today + cost + self.SAFETY_BUFFER) <= self.DAILY_LIMIT

    def spend(self, endpoint: str) -> bool:
        """
        Record spending. Returns True if budgeted, False if refused.

        Call this BEFORE making the API request. If it returns False,
        do NOT make the request.
        """
        self._check_daily_reset()
        if self.exhausted:
            return False

        cost = API_COSTS.get(endpoint, 1)
        if (self.used_today + cost) > self.DAILY_LIMIT:
            self.mark_exhausted("Would exceed daily limit")
            return False

        with self._lock:
            self.used_today += cost
            self._save_state()

        # Warn when approaching the limit
        if self.used_today > self.DAILY_LIMIT * 0.8 and self.used_today - cost <= self.DAILY_LIMIT * 0.8:
            self._log(
                f"80% of daily YouTube quota used ({self.used_today}/{self.DAILY_LIMIT}).",
                "WARNING"
            )
        return True

    def mark_exhausted(self, reason: str = "API returned quotaExceeded"):
        """Mark quota as exhausted until next Pacific midnight."""
        if self.exhausted:
            return  # already marked — don't spam logs

        with self._lock:
            self.exhausted = True
            self.exhausted_until = self._next_reset_datetime()
            self._save_state()

        wait_hours = (self.exhausted_until - datetime.now(timezone.utc)).total_seconds() / 3600
        self._log(
            f"YouTube API quota exhausted ({reason}). "
            f"All API calls paused until ~{self.exhausted_until.astimezone().strftime('%H:%M %Z')} "
            f"(~{wait_hours:.1f}h from now).",
            "ERROR"
        )

    def is_exhausted(self) -> bool:
        """Check current exhaustion state (also triggers reset check)."""
        self._check_daily_reset()
        return self.exhausted

    def seconds_until_reset(self) -> int:
        """Seconds until the next Pacific midnight reset."""
        now = datetime.now(timezone.utc)
        next_reset = self._next_reset_datetime()
        return max(0, int((next_reset - now).total_seconds()))

    def status(self) -> dict:
        """Snapshot of the current quota state."""
        self._check_daily_reset()
        return {
            'used': self.used_today,
            'limit': self.DAILY_LIMIT,
            'remaining': max(0, self.DAILY_LIMIT - self.used_today),
            'exhausted': self.exhausted,
            'reset_in_seconds': self.seconds_until_reset(),
            'reset_at': self._next_reset_datetime().isoformat(),
        }

    def handle_api_error(self, exception) -> bool:
        """
        Inspect an exception. If it's a quota-exceeded error, mark the
        manager exhausted and return True. Otherwise return False.
        """
        err = str(exception)
        if 'quotaExceeded' in err or 'quota' in err.lower() and '403' in err:
            self.mark_exhausted("API returned quotaExceeded")
            return True
        return False

    # ── Internal helpers ──────────────────────────────────────────

    def _next_reset_datetime(self) -> datetime:
        """
        Returns the next midnight Pacific Time as a timezone-aware UTC datetime.
        Midnight PT is 07:00 UTC (PST) or 08:00 UTC (PDT). We approximate with
        an 8-hour offset which is conservative — an extra hour of wait is
        better than firing requests too early.
        """
        now = datetime.now(timezone.utc)
        # Pacific midnight happens at roughly 08:00 UTC (using PDT as worst case)
        today_reset = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now < today_reset:
            return today_reset
        return today_reset + timedelta(days=1)

    def _current_pacific_day(self) -> str:
        """Return today's date in Pacific Time as YYYY-MM-DD."""
        # Approximate: subtract 8 hours from UTC to get a rough PT-anchored day
        pt_now = datetime.now(timezone.utc) - timedelta(hours=8)
        return pt_now.strftime('%Y-%m-%d')

    def _check_daily_reset(self):
        """Reset counters if we've crossed midnight PT since last call."""
        today = self._current_pacific_day()
        if self.last_reset_day != today:
            with self._lock:
                # First run of a new Pacific day — clear everything
                self.used_today = 0
                self.exhausted = False
                self.exhausted_until = None
                self.last_reset_day = today
                self._save_state()
            self._log("New Pacific day — YouTube quota reset to 0.", "SUCCESS")

    def _save_state(self):
        """Persist quota state to disk."""
        try:
            state = {
                'used_today': self.used_today,
                'exhausted': self.exhausted,
                'last_reset_day': self.last_reset_day,
                'exhausted_until': self.exhausted_until.isoformat() if self.exhausted_until else None,
            }
            self.STATE_FILE.write_text(json.dumps(state, indent=2))
        except Exception as e:
            self._log(f"Could not persist quota state: {e}", "WARNING")

    def _load_state(self):
        """Restore quota state from disk if present."""
        if not self.STATE_FILE.exists():
            self.last_reset_day = self._current_pacific_day()
            return
        try:
            state = json.loads(self.STATE_FILE.read_text())
            self.used_today = state.get('used_today', 0)
            self.exhausted = state.get('exhausted', False)
            self.last_reset_day = state.get('last_reset_day') or self._current_pacific_day()
            exh = state.get('exhausted_until')
            self.exhausted_until = datetime.fromisoformat(exh) if exh else None
        except Exception:
            self.last_reset_day = self._current_pacific_day()


# ── Convenience decorator ─────────────────────────────────────────

def quota_aware(endpoint: str):
    """
    Decorator that budgets a YouTube API call through the QuotaManager.

    If the daily budget is spent, the wrapped function returns None instead
    of hitting the API. If the call raises a quotaExceeded error, the
    manager is marked exhausted so every other module stops too.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            qm = QuotaManager.get_instance()
            if not qm.spend(endpoint):
                return None
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if qm.handle_api_error(e):
                    return None
                raise
        return wrapper
    return decorator
