# -*- coding: utf-8 -*-
"""
RealE Tube - Content Lifecycle Management Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from datetime import datetime, timedelta

import customtkinter as ctk

from database.db import DatabaseManager
from gui.tooltip import under_construction_badge


class LifecycleTab:
    """Analyses the lifecycle stage of every tracked video and surfaces
    re-optimisation opportunities.

    Partially functional -- evergreen detection and age-bucket breakdowns
    work against real DB data; re-optimisation suggestions are heuristic.
    """

    # Age buckets (label, max_days)  -- None means "no upper bound"
    AGE_BUCKETS = [
        ("< 7 days", 7),
        ("7 - 30 days", 30),
        ("30 - 90 days", 90),
        ("90+ days", None),
    ]

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self.create_tab()

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _parse_date(value):
        """Return a datetime from an ISO-ish string, or None."""
        if not value:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        return None

    def _age_days(self, video):
        """Return the age of a video in days, or None if unparseable."""
        dt = self._parse_date(video.get("created_at") or video.get("upload_date"))
        if dt is None:
            return None
        return (datetime.now() - dt).days

    @staticmethod
    def _safe_float(value, default=0.0):
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    # ── Main layout ───────────────────────────────────────────────

    def create_tab(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_age_breakdown(scroll)
        self._create_evergreen_section(scroll)
        self._create_reopt_section(scroll)
        self._create_recommendations(scroll)

        self.refresh_data()

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            bar,
            text="Content Lifecycle",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        ).pack(side="left")

        badge = under_construction_badge(
            bar, self.theme,
            text="Some lifecycle features are still under development.",
        )
        badge.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            bar,
            text="\u21bb Refresh",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=100, height=32, corner_radius=8,
            command=self.refresh_data,
        ).pack(side="right")

    # ── Video age breakdown ───────────────────────────────────────

    def _create_age_breakdown(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Video Age Breakdown",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        cards_row = ctk.CTkFrame(frame, fg_color="transparent")
        cards_row.pack(fill="x", padx=16, pady=(0, 16))

        self._bucket_labels = {}
        for label, _ in self.AGE_BUCKETS:
            card = ctk.CTkFrame(cards_row, fg_color=self.theme["bg_tertiary"], corner_radius=8)
            card.pack(side="left", expand=True, fill="both", padx=(0, 8))

            ctk.CTkLabel(
                card, text=label,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(anchor="w", padx=12, pady=(10, 2))

            val = ctk.CTkLabel(
                card, text="0",
                font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
                text_color=self.theme["text_primary"],
            )
            val.pack(anchor="w", padx=12, pady=(0, 10))
            self._bucket_labels[label] = val

    # ── Evergreen detection ───────────────────────────────────────

    def _create_evergreen_section(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Evergreen Content",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            frame,
            text="Videos older than 30 days that are still receiving views.",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        ).pack(anchor="w", padx=16, pady=(0, 8))

        self._evergreen_box = ctk.CTkTextbox(
            frame, height=120,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_secondary"],
        )
        self._evergreen_box.pack(fill="x", padx=16, pady=(0, 16))
        self._evergreen_box.configure(state="disabled")

    # ── Re-optimisation candidates ────────────────────────────────

    def _create_reopt_section(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Re-Optimisation Candidates",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            frame,
            text="Videos with low CTR or engagement that may benefit from a metadata refresh.",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        ).pack(anchor="w", padx=16, pady=(0, 8))

        self._reopt_box = ctk.CTkTextbox(
            frame, height=120,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_secondary"],
        )
        self._reopt_box.pack(fill="x", padx=16, pady=(0, 16))
        self._reopt_box.configure(state="disabled")

    # ── Recommendations ───────────────────────────────────────────

    def _create_recommendations(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Recommendations",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self._recs_box = ctk.CTkTextbox(
            frame, height=140,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_secondary"],
        )
        self._recs_box.pack(fill="x", padx=16, pady=(0, 16))
        self._recs_box.configure(state="disabled")

    # ── Data operations ───────────────────────────────────────────

    def refresh_data(self):
        try:
            videos = self.db.get_all_videos()
        except Exception:
            videos = []

        now = datetime.now()

        # ---- Age buckets ----
        bucket_counts = {label: 0 for label, _ in self.AGE_BUCKETS}
        for v in videos:
            age = self._age_days(v)
            if age is None:
                continue
            for label, max_d in self.AGE_BUCKETS:
                if max_d is None or age < max_d:
                    bucket_counts[label] += 1
                    break

        for label, _ in self.AGE_BUCKETS:
            self._bucket_labels[label].configure(text=str(bucket_counts[label]))

        # ---- Evergreen ----
        evergreen = []
        for v in videos:
            age = self._age_days(v)
            views = v.get("views") or 0
            if age is not None and age > 30 and views > 0:
                title = v.get("title_used") or v.get("file_path") or f"Video #{v['id']}"
                evergreen.append(f"\u2022 {title}  ({views:,} views, {age} days old)")

        self._set_textbox(
            self._evergreen_box,
            "\n".join(evergreen) if evergreen else "No evergreen videos detected yet.",
        )

        # ---- Re-optimisation ----
        reopt = []
        for v in videos:
            ctr = self._safe_float(v.get("ctr"))
            eng = self._safe_float(v.get("engagement_rate"))
            views = v.get("views") or 0
            if views > 0 and (ctr < 3.0 or eng < 2.0):
                title = v.get("title_used") or v.get("file_path") or f"Video #{v['id']}"
                reasons = []
                if ctr < 3.0:
                    reasons.append(f"CTR {ctr:.1f}%")
                if eng < 2.0:
                    reasons.append(f"Engagement {eng:.1f}%")
                reopt.append(f"\u2022 {title}  ({', '.join(reasons)})")

        self._set_textbox(
            self._reopt_box,
            "\n".join(reopt) if reopt else "No re-optimisation candidates found.",
        )

        # ---- Recommendations ----
        recs = []
        for v in reopt[:5]:
            recs.append(f"Consider updating metadata for: {v.lstrip(chr(8226)).strip()}")
        if not recs:
            recs.append("Upload and track more videos to receive lifecycle recommendations.")
        if len(videos) > 0 and not evergreen:
            recs.append(
                "None of your videos older than 30 days are receiving views. "
                "Consider refreshing titles/thumbnails for older content."
            )

        self._set_textbox(self._recs_box, "\n".join(recs))

    @staticmethod
    def _set_textbox(textbox, text):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")
