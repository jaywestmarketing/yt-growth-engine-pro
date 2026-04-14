# -*- coding: utf-8 -*-
"""
RealE Tube - Auto-Optimizer Tab
Unified interface for lifecycle optimization, smart scheduling, and analytics
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager
from datetime import datetime


class AutoOptimizerTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        # Components (lazy-loaded)
        self.lifecycle_optimizer = None
        self.smart_scheduler = None
        self.analytics_fetcher = None

        self._create_ui()

    def _create_ui(self):
        t = self.theme
        main = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Header ───────────────────────────────────────────────────
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            header,
            text="Recommendations & Automation",
            font=(t["font_family"], t["font_size_heading"], "bold"),
            text_color=t["text_primary"],
        ).pack(side="left")
        badge = under_construction_badge(
            header, t,
            text="Advanced automation features. Use with caution on production videos."
        )
        badge.pack(side="left", padx=(8, 0))

        # ── Lifecycle Optimizer ──────────────────────────────────────
        sec = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        sec.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            sec,
            text="Lifecycle Optimizer",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            sec,
            text="Automatically detect and refresh underperforming videos.",
            font=(t["font_family"], t["font_size_small"]),
            text_color=t["text_tertiary"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

        btns = ctk.CTkFrame(sec, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            btns,
            text="Find Candidates",
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"],
            hover_color=t["accent_hover"],
            text_color="#FFFFFF",
            height=32,
            corner_radius=6,
            command=self._show_reopt_candidates,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns,
            text="Preview Changes",
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["button_bg"],
            hover_color=t["button_hover"],
            text_color="#FFFFFF",
            height=32,
            corner_radius=6,
            command=self._preview_reopt,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns,
            text="Apply (Dry-Run)",
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["warning"],
            hover_color=t["warning"],
            text_color="#FFFFFF",
            height=32,
            corner_radius=6,
            command=self._apply_reopt_dryrun,
        ).pack(side="left")

        self._reopt_info = ctk.CTkTextbox(
            sec, height=100,
            font=(t["font_family"], t["font_size_small"]),
            fg_color=t["bg_tertiary"],
            text_color=t["text_secondary"],
        )
        self._reopt_info.pack(fill="x", padx=16, pady=(0, 16))
        self._reopt_info.configure(state="disabled")

        # ── Smart Scheduler ──────────────────────────────────────────
        sec = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        sec.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            sec,
            text="Smart Scheduler",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            sec,
            text="Schedule uploads for optimal posting times based on your analytics.",
            font=(t["font_family"], t["font_size_small"]),
            text_color=t["text_tertiary"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

        btns = ctk.CTkFrame(sec, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            btns,
            text="Analyze Timing",
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"],
            hover_color=t["accent_hover"],
            text_color="#FFFFFF",
            height=32,
            corner_radius=6,
            command=self._analyze_timing,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns,
            text="Get Suggestions",
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["button_bg"],
            hover_color=t["button_hover"],
            text_color="#FFFFFF",
            height=32,
            corner_radius=6,
            command=self._get_schedule_suggestions,
        ).pack(side="left")

        self._scheduler_info = ctk.CTkTextbox(
            sec, height=100,
            font=(t["font_family"], t["font_size_small"]),
            fg_color=t["bg_tertiary"],
            text_color=t["text_secondary"],
        )
        self._scheduler_info.pack(fill="x", padx=16, pady=(0, 16))
        self._scheduler_info.configure(state="disabled")

        # ── Analytics ────────────────────────────────────────────────
        sec = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        sec.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            sec,
            text="Advanced Analytics",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            sec,
            text="Fetch channel statistics and video-level insights.",
            font=(t["font_family"], t["font_size_small"]),
            text_color=t["text_tertiary"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

        btns = ctk.CTkFrame(sec, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            btns,
            text="Channel Stats",
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"],
            hover_color=t["accent_hover"],
            text_color="#FFFFFF",
            height=32,
            corner_radius=6,
            command=self._get_channel_stats,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns,
            text="Performance Summary",
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["button_bg"],
            hover_color=t["button_hover"],
            text_color="#FFFFFF",
            height=32,
            corner_radius=6,
            command=self._get_summary,
        ).pack(side="left")

        self._analytics_info = ctk.CTkTextbox(
            sec, height=100,
            font=(t["font_family"], t["font_size_small"]),
            fg_color=t["bg_tertiary"],
            text_color=t["text_secondary"],
        )
        self._analytics_info.pack(fill="x", padx=16, pady=(0, 16))
        self._analytics_info.configure(state="disabled")

    def _init_components(self):
        """Lazy-load automation components"""
        if self.lifecycle_optimizer is not None:
            return

        try:
            from automation.lifecycle_optimizer import LifecycleOptimizer
            from automation.smart_scheduler import SmartScheduler
            from automation.analytics_fetcher import AnalyticsFetcher
            from automation.google_auth import GoogleAuthHelper
            from pathlib import Path
            import json

            config_path = Path(__file__).parent.parent / "config" / "config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)

                youtube_creds = config['api'].get('youtube_credentials')
                ai_key = config['api'].get('ai_api_key')
                youtube_service = None

                if youtube_creds and Path(youtube_creds).exists():
                    auth = GoogleAuthHelper(youtube_creds)
                    youtube_service = auth.get_youtube_service()

                self.lifecycle_optimizer = LifecycleOptimizer(youtube_service, ai_key)
                self.smart_scheduler = SmartScheduler()
                self.analytics_fetcher = AnalyticsFetcher(youtube_service)
        except Exception as e:
            print(f"Error initializing components: {e}")

    def _show_reopt_candidates(self):
        """Find and display reoptimization candidates"""
        self._init_components()
        if not self.lifecycle_optimizer:
            self._set_text(self._reopt_info, "Components not initialized. Check credentials.")
            return

        try:
            candidates = self.lifecycle_optimizer.find_reoptimization_candidates()
            if not candidates:
                self._set_text(self._reopt_info, "No reoptimization candidates found. All videos performing well!")
                return

            text = f"Found {len(candidates)} underperforming videos:\n\n"
            for v in candidates[:10]:  # Show top 10
                title = v.get('title_used', v.get('file_path', f"ID {v['id']}"))
                reasons = v.get('reopt_reasons', [])
                text += f"• {title}\n  {', '.join(reasons)}\n\n"

            self._set_text(self._reopt_info, text)
        except Exception as e:
            self._set_text(self._reopt_info, f"Error: {str(e)}")

    def _preview_reopt(self):
        """Preview what changes would be made"""
        self._init_components()
        if not self.lifecycle_optimizer:
            self._set_text(self._reopt_info, "Components not initialized.")
            return

        try:
            result = self.lifecycle_optimizer.batch_reoptimize(max_videos=3, dry_run=True)
            text = f"Preview: {result['successful']} videos would be reoptimized\n\n"
            for change in result['changes'][:5]:
                text += f"• {change.get('title', 'Unknown')}\n"
                text += f"  Reasons: {', '.join(change.get('reasons', []))}\n\n"

            self._set_text(self._reopt_info, text)
        except Exception as e:
            self._set_text(self._reopt_info, f"Error: {str(e)}")

    def _apply_reopt_dryrun(self):
        """Apply reoptimization (actual changes, not dry-run)"""
        self._init_components()
        if not self.lifecycle_optimizer:
            self._set_text(self._reopt_info, "Components not initialized.")
            return

        try:
            result = self.lifecycle_optimizer.batch_reoptimize(max_videos=2, dry_run=False)
            text = f"Applied changes to {result['successful']}/{result['attempted']} videos\n\n"
            for change in result['changes']:
                text += f"✓ Updated: {change.get('old_title', 'Unknown')}\n"
                text += f"  New keywords: {len(change.get('new_keywords', []))} tags\n\n"

            self._set_text(self._reopt_info, text)
        except Exception as e:
            self._set_text(self._reopt_info, f"Error: {str(e)}")

    def _analyze_timing(self):
        """Analyze optimal posting times"""
        self._init_components()
        if not self.smart_scheduler:
            self._set_text(self._scheduler_info, "Scheduler not initialized.")
            return

        try:
            optimal = self.smart_scheduler.find_optimal_times()
            text = f"Analyzed {optimal.get('total_videos_analyzed', 0)} videos\n\n"

            if optimal['best_time']:
                day, hour = optimal['best_time']
                text += f"Best posting time: {day} at {hour:02d}:00\n\n"

            text += "Top posting hours:\n"
            for h in sorted(optimal['hours'].keys())[:5]:
                text += f"  {h:02d}:00 - avg {optimal['hours'][h]:,.0f} views\n"

            self._set_text(self._scheduler_info, text)
        except Exception as e:
            self._set_text(self._scheduler_info, f"Error: {str(e)}")

    def _get_schedule_suggestions(self):
        """Get upload schedule suggestions"""
        self._init_components()
        if not self.smart_scheduler:
            self._set_text(self._scheduler_info, "Scheduler not initialized.")
            return

        try:
            suggestions = self.smart_scheduler.suggest_schedule(num_suggestions=5)
            text = "Suggested upload times:\n\n"

            for idx, (dt_str, reason) in enumerate(suggestions, 1):
                text += f"{idx}. {dt_str}\n   {reason}\n\n"

            self._set_text(self._scheduler_info, text)
        except Exception as e:
            self._set_text(self._scheduler_info, f"Error: {str(e)}")

    def _get_channel_stats(self):
        """Fetch channel statistics"""
        self._init_components()
        if not self.analytics_fetcher:
            self._set_text(self._analytics_info, "Analytics not initialized.")
            return

        try:
            stats = self.analytics_fetcher.get_channel_statistics()
            if not stats:
                self._set_text(self._analytics_info, "Could not fetch channel statistics.")
                return

            text = f"{stats['channel_name']}\n\n"
            text += f"Subscribers: {stats['subscriber_count']:,}\n"
            text += f"Total Views: {stats['view_count']:,}\n"
            text += f"Videos Uploaded: {stats['video_count']}\n"

            self._set_text(self._analytics_info, text)
        except Exception as e:
            self._set_text(self._analytics_info, f"Error: {str(e)}")

    def _get_summary(self):
        """Get performance summary"""
        self._init_components()
        if not self.analytics_fetcher:
            self._set_text(self._analytics_info, "Analytics not initialized.")
            return

        try:
            summary = self.analytics_fetcher.get_performance_summary()
            if not summary:
                self._set_text(self._analytics_info, "No data available.")
                return

            text = f"Videos Tracked: {summary['total_videos_tracked']}\n"
            text += f"Total Views: {summary['total_views']:,}\n"
            text += f"Avg Views/Video: {summary['avg_views_per_video']:,.0f}\n"
            text += f"Avg Engagement: {summary['avg_engagement_rate']:.2f}%\n"
            text += f"Like Rate: {summary['overall_like_rate']:.2f}%\n"
            text += f"Comment Rate: {summary['overall_comment_rate']:.2f}%\n"

            self._set_text(self._analytics_info, text)
        except Exception as e:
            self._set_text(self._analytics_info, f"Error: {str(e)}")

    @staticmethod
    def _set_text(textbox, text):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")
