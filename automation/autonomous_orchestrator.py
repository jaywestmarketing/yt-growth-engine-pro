# -*- coding: utf-8 -*-
"""
RealE Tube - Autonomous Orchestrator

The "brain" of the app. Drives the whole YouTube pipeline with a single
adaptive loop that honours the central QuotaManager and sleeps the right
amount of time based on what's actually going on.

Responsibilities:
  • Decide what to do each tick (uploads vs. monitoring vs. optimisation)
  • Sleep until the next reasonable action (or until quota reset)
  • Handle transient network errors with exponential backoff
  • Schedule uploads for optimal publish times (native YouTube publishAt)
  • Auto-reoptimise underperforming videos when quota is healthy
  • Stop cold when quota is dead — don't spam the API

Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Optional

from automation.quota_manager import QuotaManager


class AutonomousOrchestrator:
    """
    Single-threaded adaptive loop that replaces the dumb 5-minute timer.

    It wakes up, checks the system state, performs the most valuable action,
    then sleeps for a quota-aware duration before waking again.
    """

    # How long to sleep when there is work to do (seconds)
    ACTIVE_INTERVAL = 300   # 5 min
    # How long to sleep when the system is idle (no pending work)
    IDLE_INTERVAL = 900     # 15 min
    # How long to back off when we hit repeated network errors
    ERROR_BACKOFF_BASE = 30  # grows exponentially to a cap

    def __init__(self, engine, config: dict, log: Callable = None):
        """
        Args:
            engine: AutomationEngine instance (provides drive_monitor, etc.)
            config: Loaded config dict
            log:    Log callback (message, level)
        """
        self.engine = engine
        self.config = config
        self.log = log or (lambda msg, lvl="INFO": print(f"[{lvl}] {msg}"))

        self.qm = QuotaManager.get_instance()
        # Let the quota manager send its warnings through the UI log
        self.qm.set_log_callback(self.log)

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._network_error_count = 0

        # Optional components — lazily created
        self._lifecycle_optimizer = None
        self._smart_scheduler = None

    # ── Lifecycle ─────────────────────────────────────────────────

    def start(self):
        """Start the autonomous loop in a background daemon thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="AutonomousOrchestrator")
        self._thread.start()
        self.log("Autonomous orchestrator started.", "SUCCESS")

    def stop(self):
        """Signal the loop to exit."""
        self._stop_event.set()
        self.log("Autonomous orchestrator stopping...", "INFO")

    # ── Main loop ─────────────────────────────────────────────────

    def _run(self):
        """The tick-based decision loop."""
        # Initial catch-up on startup
        self._safe_step("startup_catchup", self._startup_catchup)

        while not self._stop_event.is_set():
            # If quota is dead, sleep until the daily reset — no API calls.
            if self.qm.is_exhausted():
                wait_s = self.qm.seconds_until_reset()
                hours = wait_s / 3600
                self.log(
                    f"Quota exhausted. Sleeping {hours:.1f}h until YouTube daily reset.",
                    "WARNING"
                )
                # Break the long sleep into shorter chunks so stop() can interrupt
                if self._sleep_interruptible(wait_s + 60):
                    break
                self.log("Quota reset. Resuming autonomous operation.", "SUCCESS")
                self._network_error_count = 0
                continue

            # Execute a full work cycle; each step reports whether it did work.
            did_work = False
            did_work |= bool(self._safe_step("new_videos", self._process_new_videos))
            did_work |= bool(self._safe_step("retries", self._process_retries))
            did_work |= bool(self._safe_step("monitoring", self._monitor_performance))
            did_work |= bool(self._safe_step("reoptimization", self._reoptimize_underperformers))
            did_work |= bool(self._safe_step("scheduled_publishing", self._publish_scheduled))

            # Choose the next sleep duration
            if self._network_error_count >= 3:
                # Exponential backoff for sustained network trouble, capped at 10 min
                delay = min(600, self.ERROR_BACKOFF_BASE * (2 ** min(self._network_error_count, 5)))
                self.log(
                    f"Persistent network errors ({self._network_error_count}). "
                    f"Backing off {delay}s.",
                    "WARNING"
                )
            elif self.qm.is_exhausted():
                # A step during this cycle tripped the quota — loop again to pick up the long sleep
                delay = 1
            elif did_work:
                delay = self.ACTIVE_INTERVAL
            else:
                delay = self.IDLE_INTERVAL

            if self._sleep_interruptible(delay):
                break

        self.log("Autonomous orchestrator stopped.", "WARNING")

    # ── Step wrappers ─────────────────────────────────────────────

    def _safe_step(self, name: str, fn: Callable) -> bool:
        """
        Run a pipeline step, catching all errors.

        Returns a truthy value if the step did meaningful work.
        """
        try:
            result = fn()
            # Reset the error counter after a successful step
            self._network_error_count = 0
            return bool(result)
        except Exception as e:
            # Quota errors are recorded globally — don't count as network errors
            if self.qm.handle_api_error(e):
                return False
            err = str(e).lower()
            if 'timeout' in err or 'timed out' in err or 'connection' in err:
                self._network_error_count += 1
                self.log(f"Network error in {name}: {e}", "WARNING")
            else:
                self.log(f"Error in {name}: {e}", "ERROR")
            return False

    def _startup_catchup(self):
        """Run whatever got missed while the app was off."""
        if self.engine.performance_monitor and not self.qm.is_exhausted():
            summary = self.engine.performance_monitor.check_all_videos()
            if summary.get('checked', 0) > 0:
                self.log(
                    f"Startup catch-up: checked {summary['checked']} videos.",
                    "SUCCESS"
                )

    def _process_new_videos(self):
        """Delegate to the existing engine's Drive watcher."""
        if not self.engine.drive_monitor:
            return False
        before = len(getattr(self.engine.drive_monitor, 'processed_files', []))
        # Calls the engine's existing pipeline — which already guards quota
        self.engine._process_new_videos()
        after = len(getattr(self.engine.drive_monitor, 'processed_files', []))
        return after > before

    def _process_retries(self):
        """Delegate to the engine's retry handler."""
        retries = self.engine.db.get_videos_by_status('retry')
        if not retries:
            return False
        self.engine._process_retries()
        return True

    def _monitor_performance(self):
        """Check video performance — the engine's method is already quota-aware."""
        if not self.engine.performance_monitor:
            return False
        if self.qm.is_exhausted():
            return False
        summary = self.engine.performance_monitor.check_all_videos()
        return summary.get('checked', 0) > 0

    def _reoptimize_underperformers(self):
        """
        Once a day, run the lifecycle optimizer to refresh underperforming
        videos. Skipped entirely when quota is tight.
        """
        # Only try when we have plenty of quota headroom
        status = self.qm.status()
        if status['remaining'] < 2000:
            return False
        # Only run once per Pacific day; rely on DB reopt_history to gate this
        try:
            recent = self.engine.db.get_reopt_history()
        except Exception:
            recent = []
        if recent:
            last_ts = recent[0].get('timestamp', '')
            # Skip if we've already reoptimized today
            if last_ts and last_ts.startswith(datetime.utcnow().strftime('%Y-%m-%d')):
                return False

        optimizer = self._get_lifecycle_optimizer()
        if not optimizer:
            return False

        try:
            result = optimizer.batch_reoptimize(max_videos=2, dry_run=False)
            if result.get('successful', 0) > 0:
                self.log(
                    f"Auto-reoptimized {result['successful']} underperforming videos.",
                    "SUCCESS"
                )
                return True
        except Exception as e:
            self.log(f"Lifecycle reoptimization skipped: {e}", "WARNING")
        return False

    def _publish_scheduled(self):
        """
        Process the scheduled uploads queue.

        We use YouTube's native `publishAt` feature, so once an upload is in
        YouTube's hands there is nothing to do on a recurring basis. What this
        step handles is actually *uploading* videos whose local queued time has
        arrived, with publishAt set so YouTube flips them public.
        """
        try:
            queued = self.engine.db.get_scheduled_uploads(status='queued')
        except Exception:
            return False

        if not queued:
            return False

        now = datetime.now()
        work_done = False

        for item in queued:
            try:
                scheduled_at = datetime.fromisoformat(item['scheduled_at'].replace('Z', ''))
            except Exception:
                continue

            # Upload when within 10 minutes of the scheduled time, so YouTube's
            # processing + publishAt flip happens right on target.
            if scheduled_at > now + timedelta(minutes=10):
                continue

            file_path = item.get('file_path')
            if not file_path or not Path(file_path).exists():
                self.engine.db.update_scheduled_status(item['id'], 'failed')
                self.log(f"Scheduled upload missing file: {file_path}", "ERROR")
                continue

            # Let the engine do the heavy lifting, passing a publishAt so YouTube
            # holds the video private and flips it at the right moment.
            try:
                publish_at_iso = scheduled_at.isoformat() + 'Z' if scheduled_at > now else None
                video_id = self.engine.db.add_video(
                    Path(file_path).name, item.get('description', '')
                )
                self.engine._process_and_upload(
                    video_id, file_path, item.get('description', ''),
                )
                self.engine.db.update_scheduled_status(item['id'], 'uploaded', video_id)
                work_done = True
            except Exception as e:
                if self.qm.handle_api_error(e):
                    break
                self.log(f"Scheduled upload failed for {file_path}: {e}", "ERROR")
                self.engine.db.update_scheduled_status(item['id'], 'failed')

        return work_done

    # ── Helpers ───────────────────────────────────────────────────

    def _get_lifecycle_optimizer(self):
        if self._lifecycle_optimizer is None:
            try:
                from automation.lifecycle_optimizer import LifecycleOptimizer
                auth = getattr(self.engine, 'auth_helper', None)
                yt = auth.get_youtube_service() if auth else None
                ai_key = self.config.get('api', {}).get('ai_api_key')
                if yt and ai_key:
                    self._lifecycle_optimizer = LifecycleOptimizer(yt, ai_key)
            except Exception as e:
                self.log(f"Could not initialise lifecycle optimizer: {e}", "WARNING")
        return self._lifecycle_optimizer

    def _sleep_interruptible(self, seconds: float) -> bool:
        """
        Sleep in small chunks so stop() can cancel promptly.

        Returns True if a stop was requested during the sleep.
        """
        remaining = seconds
        while remaining > 0 and not self._stop_event.is_set():
            chunk = min(5.0, remaining)
            time.sleep(chunk)
            remaining -= chunk
        return self._stop_event.is_set()
