# -*- coding: utf-8 -*-
"""
RealE Tube - Analytics Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from database.db import DatabaseManager


class AnalyticsTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        # References to dynamic widgets for refresh
        self._metric_value_labels = {}
        self._keywords_container = None
        self._status_bars = {}
        self._chart_container = None

        self.create_analytics()

    # ── Helpers ────────────────────────────────────────────────────

    def _safe_float(self, value, default=0.0):
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value, default=0):
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    # ── Layout ────────────────────────────────────────────────────

    def create_analytics(self):
        """Create analytics layout"""
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Refresh header
        self._create_refresh_header(main_frame)

        # Scrollable content area
        scroll = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True)

        self.create_overall_stats(scroll)
        self.create_status_breakdown(scroll)
        self.create_charts_section(scroll)
        self.create_keywords_section(scroll)

    def _create_refresh_header(self, parent):
        """Create a thin header bar with a refresh button."""
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="Analytics",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title.pack(side="left")

        btn = ctk.CTkButton(
            bar,
            text="↻ Refresh",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=100,
            height=32,
            corner_radius=8,
            command=self.refresh_analytics
        )
        btn.pack(side="right")

    # ── Overall stats ─────────────────────────────────────────────

    def create_overall_stats(self, parent):
        """Create overall statistics section"""
        stats_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        stats_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            stats_frame,
            text="Overall Performance",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title.pack(fill="x", padx=20, pady=(20, 15))

        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=(0, 20))
        stats_container.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Load stats
        stats = self._load_stats()

        metrics = [
            ("success_rate", "Success Rate", stats["success_rate_str"], "Videos meeting thresholds", self.theme["success"]),
            ("avg_attempts", "Avg Attempts", stats["avg_attempts_str"], "Average retries to success", self.theme["accent"]),
            ("total_videos", "Total Videos", stats["total_videos_str"], "All-time processed", self.theme["text_primary"]),
            ("avg_views", "Avg Views", stats["avg_views_str"], "Mean views per video", self.theme["accent"]),
            ("avg_engagement", "Avg Engagement", stats["avg_engagement_str"], "Mean engagement %", self.theme["success"]),
        ]

        for col, (key, mtitle, mvalue, mdesc, mcolor) in enumerate(metrics):
            self._create_metric_card(stats_container, key, mtitle, mvalue, mdesc, mcolor, col)

    def _create_metric_card(self, parent, key, title, value, description, color, column):
        """Create individual metric card, storing the value label for refresh."""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_tertiary"],
            corner_radius=8
        )
        card.grid(row=0, column=column, padx=8, sticky="ew")

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(self.theme["font_family"], 32, "bold"),
            text_color=color
        )
        value_label.pack(pady=(18, 4))
        self._metric_value_labels[key] = value_label

        ctk.CTkLabel(
            card,
            text=title,
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_secondary"]
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            card,
            text=description,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"]
        ).pack(pady=(0, 18))

    # ── Status breakdown ──────────────────────────────────────────

    def create_status_breakdown(self, parent):
        """Visual bar breakdown of video statuses."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            frame, text="Status Breakdown",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"], anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))

        self._status_container = ctk.CTkFrame(frame, fg_color="transparent")
        self._status_container.pack(fill="x", padx=20, pady=(0, 20))

        self._render_status_bars()

    def _render_status_bars(self):
        """Draw horizontal bars representing each status count."""
        for w in self._status_container.winfo_children():
            w.destroy()

        stats = self._load_stats()
        by_status = stats["by_status"]
        total = max(sum(by_status.values()), 1)

        color_map = {
            "pending": self.theme["text_tertiary"],
            "uploaded": self.theme["accent"],
            "monitoring": self.theme["accent"],
            "success": self.theme["success"],
            "retry": self.theme["warning"],
            "abandoned": self.theme["error"],
        }

        for i, (status, count) in enumerate(sorted(by_status.items())):
            row = ctk.CTkFrame(self._status_container, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row, text=f"{status.title()} ({count})",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"], width=130, anchor="w"
            ).pack(side="left")

            bar_bg = ctk.CTkFrame(row, fg_color=self.theme["bg_tertiary"], height=16, corner_radius=4)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(5, 0))
            bar_bg.pack_propagate(False)

            pct = count / total
            bar_color = color_map.get(status, self.theme["accent"])
            if pct > 0:
                bar_fill = ctk.CTkFrame(bar_bg, fg_color=bar_color, corner_radius=4)
                bar_fill.place(relx=0, rely=0, relwidth=max(pct, 0.02), relheight=1.0)

    # ── Charts section ────────────────────────────────────────────

    def create_charts_section(self, parent):
        """Create performance over time section with text-based chart."""
        charts_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        charts_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            charts_frame,
            text="Performance Over Time",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))

        self._chart_container = ctk.CTkFrame(
            charts_frame,
            fg_color=self.theme["bg_tertiary"],
            corner_radius=8,
            height=220
        )
        self._chart_container.pack(fill="x", padx=20, pady=(0, 20))
        self._chart_container.pack_propagate(False)

        self._render_chart()

    def _render_chart(self):
        """Render a simple text-based performance summary inside the chart area."""
        for w in self._chart_container.winfo_children():
            w.destroy()

        try:
            videos = self.db.get_all_videos()
            if not videos:
                raise ValueError("No data")

            # Group by month
            monthly = {}
            for v in videos:
                date_str = v.get('upload_date') or v.get('created_at') or ''
                month_key = date_str[:7] if date_str else 'Unknown'
                if month_key not in monthly:
                    monthly[month_key] = {"count": 0, "views": 0, "success": 0}
                monthly[month_key]["count"] += 1
                monthly[month_key]["views"] += self._safe_int(v.get('views'))
                if v.get('status') == 'success':
                    monthly[month_key]["success"] += 1

            if not monthly or list(monthly.keys()) == ['Unknown']:
                raise ValueError("No date data")

            # Display monthly summary
            header = ctk.CTkFrame(self._chart_container, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 5))

            for col_text, w in [("Month", 100), ("Videos", 80), ("Views", 80), ("Success", 80), ("Avg Views", 90)]:
                ctk.CTkLabel(
                    header, text=col_text, width=w,
                    font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                    text_color=self.theme["text_secondary"], anchor="w"
                ).pack(side="left", padx=5)

            for month_key in sorted(monthly.keys(), reverse=True)[:8]:
                data = monthly[month_key]
                avg_views = data["views"] // max(data["count"], 1)
                row = ctk.CTkFrame(self._chart_container, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=1)

                for val, w in [(month_key, 100), (str(data["count"]), 80),
                               (str(data["views"]), 80), (str(data["success"]), 80),
                               (str(avg_views), 90)]:
                    ctk.CTkLabel(
                        row, text=val, width=w,
                        font=(self.theme["font_family"], self.theme["font_size_small"]),
                        text_color=self.theme["text_primary"], anchor="w"
                    ).pack(side="left", padx=5)

        except Exception:
            placeholder = ctk.CTkLabel(
                self._chart_container,
                text="Upload videos to see performance trends\n\nTracks: monthly uploads, views, success rate",
                font=(self.theme["font_family"], self.theme["font_size_body"]),
                text_color=self.theme["text_tertiary"],
                justify="center"
            )
            placeholder.place(relx=0.5, rely=0.5, anchor="center")

    # ── Keywords section ──────────────────────────────────────────

    def create_keywords_section(self, parent):
        """Create top keywords section"""
        keywords_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        keywords_frame.pack(fill="x")

        ctk.CTkLabel(
            keywords_frame,
            text="Best Performing Keywords",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))

        self._keywords_container = ctk.CTkFrame(keywords_frame, fg_color="transparent")
        self._keywords_container.pack(fill="x", padx=20, pady=(0, 20))

        self._render_keywords()

    def _render_keywords(self):
        """Populate the keywords container from database."""
        for w in self._keywords_container.winfo_children():
            w.destroy()

        try:
            top_keywords = self.db.get_top_keywords(limit=10)

            if top_keywords:
                for i, kw in enumerate(top_keywords):
                    self._create_keyword_item(
                        self._keywords_container,
                        i + 1,
                        kw['keyword'],
                        f"{self._safe_int(kw.get('video_count'))} videos",
                        f"avg {self._safe_int(kw.get('avg_views'))} views",
                        f"{self._safe_float(kw.get('avg_ctr')):.1f}% CTR"
                    )
            else:
                ctk.CTkLabel(
                    self._keywords_container,
                    text="No keyword data yet. Upload videos to see statistics.",
                    font=(self.theme["font_family"], self.theme["font_size_body"]),
                    text_color=self.theme["text_tertiary"]
                ).pack(pady=20)

        except Exception as e:
            print(f"Error loading keywords: {e}")
            ctk.CTkLabel(
                self._keywords_container,
                text="Unable to load keyword statistics.",
                font=(self.theme["font_family"], self.theme["font_size_body"]),
                text_color=self.theme["text_tertiary"]
            ).pack(pady=20)

    def _create_keyword_item(self, parent, rank, keyword, count, performance, ctr_text):
        """Create individual keyword row."""
        item_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_tertiary"],
            corner_radius=8
        )
        item_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            item_frame,
            text=f"#{rank}",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["accent"],
            width=40
        ).pack(side="left", padx=(15, 10), pady=12)

        ctk.CTkLabel(
            item_frame,
            text=keyword,
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        ).pack(side="left", padx=(0, 15), pady=12)

        ctk.CTkLabel(
            item_frame,
            text=count,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"]
        ).pack(side="left", padx=(0, 15), pady=12)

        ctk.CTkLabel(
            item_frame,
            text=ctr_text,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"]
        ).pack(side="right", padx=15, pady=12)

        ctk.CTkLabel(
            item_frame,
            text=performance,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["success"]
        ).pack(side="right", padx=(0, 10), pady=12)

    # ── Data loading ──────────────────────────────────────────────

    def _load_stats(self):
        """Load all analytics stats from DB, returning safe formatted strings."""
        try:
            stats = self.db.get_statistics()
            by_status = stats.get('by_status', {})
            total_videos = sum(by_status.values())
            success_rate = self._safe_float(stats.get('success_rate'))
            avg_attempts = self._safe_float(stats.get('avg_attempts'))

            # Compute avg views and engagement across all videos
            videos = self.db.get_all_videos()
            if videos:
                total_views = sum(self._safe_int(v.get('views')) for v in videos)
                total_eng = sum(self._safe_float(v.get('engagement_rate')) for v in videos)
                count = len(videos)
                avg_views = total_views / count
                avg_engagement = total_eng / count
            else:
                avg_views = 0
                avg_engagement = 0

        except Exception as e:
            print(f"Error loading stats: {e}")
            by_status = {}
            total_videos = 0
            success_rate = 0
            avg_attempts = 0
            avg_views = 0
            avg_engagement = 0

        return {
            "by_status": by_status,
            "total_videos": total_videos,
            "total_videos_str": str(total_videos),
            "success_rate": success_rate,
            "success_rate_str": f"{success_rate:.1f}%",
            "avg_attempts": avg_attempts,
            "avg_attempts_str": f"{avg_attempts:.1f}",
            "avg_views": avg_views,
            "avg_views_str": f"{avg_views:.0f}",
            "avg_engagement": avg_engagement,
            "avg_engagement_str": f"{avg_engagement:.1f}%",
        }

    # ── Refresh ───────────────────────────────────────────────────

    def refresh_analytics(self):
        """Refresh all analytics data from the database."""
        stats = self._load_stats()

        # Update metric cards
        updates = {
            "success_rate": stats["success_rate_str"],
            "avg_attempts": stats["avg_attempts_str"],
            "total_videos": stats["total_videos_str"],
            "avg_views": stats["avg_views_str"],
            "avg_engagement": stats["avg_engagement_str"],
        }
        for key, val in updates.items():
            if key in self._metric_value_labels:
                self._metric_value_labels[key].configure(text=val)

        # Re-render dynamic sections
        self._render_status_bars()
        self._render_chart()
        self._render_keywords()

        if hasattr(self.app, 'dashboard_tab'):
            self.app.dashboard_tab.add_log_entry("Analytics refreshed", "INFO")
