# -*- coding: utf-8 -*-
"""
RealE Tube - Trend Detection & Niche Alerts Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager

# Sample trend data shown when Google Trends API is not connected
_SAMPLE_TRENDS = [
    {"keyword": "AI video editing tools", "volume": "HIGH", "direction": "up"},
    {"keyword": "passive income 2026", "volume": "HIGH", "direction": "up"},
    {"keyword": "real estate investing tips", "volume": "MEDIUM", "direction": "steady"},
    {"keyword": "home renovation DIY", "volume": "MEDIUM", "direction": "up"},
    {"keyword": "mortgage rate predictions", "volume": "LOW", "direction": "new"},
    {"keyword": "smart home automation", "volume": "LOW", "direction": "steady"},
]

_DIRECTION_SYMBOLS = {"up": "▲", "steady": "►", "new": "★"}
_VOLUME_COLORS = {"HIGH": "#E53935", "MEDIUM": "#FB8C00", "LOW": "#43A047"}

_ALERT_TYPES = [
    ("trending_topic", "Trending topic detected"),
    ("competitor_upload", "Competitor upload alert"),
    ("keyword_spike", "Keyword search spike"),
]


class TrendDetectionTab:
    """GUI tab for trend detection and niche alert management."""

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self._alert_vars = {}
        self._trends_frame = None
        self._history_frame = None

        self._build_layout()

    # ── Layout ────────────────────────────────────────────────────

    def _build_layout(self):
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_header(main)

        scroll = ctk.CTkScrollableFrame(main, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._build_niche_config(scroll)
        self._build_alert_settings(scroll)
        self._build_trends_display(scroll)
        self._build_alert_history(scroll)

    # ── Header ────────────────────────────────────────────────────

    def _build_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="Trend Detection & Niche Alerts",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(side="left")

        badge = under_construction_badge(bar, self.theme)
        badge.pack(side="left", padx=(8, 0))

        btn = ctk.CTkButton(
            bar,
            text="↻ Refresh",
            width=90,
            height=30,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            command=self.refresh,
        )
        btn.pack(side="right")

    # ── Niche Configuration ───────────────────────────────────────

    def _build_niche_config(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Niche Keywords",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=14, pady=(12, 4))

        ctk.CTkLabel(
            frame,
            text="Enter comma-separated keywords to track trends in your niche",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        ).pack(anchor="w", padx=14)

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(6, 12))

        self._keywords_entry = ctk.CTkEntry(
            row,
            placeholder_text="e.g. real estate, investing, home renovation",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            height=34,
        )
        self._keywords_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            row,
            text="Save",
            width=70,
            height=34,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            command=self._save_keywords,
        ).pack(side="right")

    def _save_keywords(self):
        """Persist niche keywords (placeholder action)."""
        pass

    # ── Alert Settings ────────────────────────────────────────────

    def _build_alert_settings(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Alert Settings",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=14, pady=(12, 6))

        for key, label in _ALERT_TYPES:
            var = ctk.BooleanVar(value=True)
            self._alert_vars[key] = var
            ctk.CTkCheckBox(
                frame,
                text=label,
                variable=var,
                font=(self.theme["font_family"], self.theme["font_size_body"]),
                text_color=self.theme["text_secondary"],
                fg_color=self.theme["accent"],
                hover_color=self.theme["accent_hover"],
            ).pack(anchor="w", padx=20, pady=3)

        # Bottom padding
        ctk.CTkFrame(frame, fg_color="transparent", height=8).pack()

    # ── Detected Trends ──────────────────────────────────────────

    def _build_trends_display(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Detected Trends",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=14, pady=(12, 2))

        # API notice
        ctk.CTkLabel(
            frame,
            text="Connect Google Trends API in Settings to enable live trend detection",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["warning"],
        ).pack(anchor="w", padx=14, pady=(0, 8))

        self._trends_frame = ctk.CTkScrollableFrame(
            frame, fg_color="transparent", height=240
        )
        self._trends_frame.pack(fill="x", padx=10, pady=(0, 10))

        self._populate_trends(_SAMPLE_TRENDS)

    def _populate_trends(self, trends):
        """Render trend cards inside the scrollable trends frame."""
        for widget in self._trends_frame.winfo_children():
            widget.destroy()

        for trend in trends:
            self._create_trend_card(self._trends_frame, trend)

    def _create_trend_card(self, parent, trend):
        card = ctk.CTkFrame(parent, fg_color=self.theme["bg_tertiary"], corner_radius=8)
        card.pack(fill="x", pady=3)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        # Direction symbol
        symbol = _DIRECTION_SYMBOLS.get(trend["direction"], "?")
        ctk.CTkLabel(
            inner,
            text=symbol,
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["accent"],
            width=24,
        ).pack(side="left")

        # Keyword
        ctk.CTkLabel(
            inner,
            text=trend["keyword"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_primary"],
        ).pack(side="left", padx=(6, 12))

        # Volume badge
        vol = trend["volume"]
        ctk.CTkLabel(
            inner,
            text=f" {vol} ",
            font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
            text_color="#FFFFFF",
            fg_color=_VOLUME_COLORS.get(vol, self.theme["accent"]),
            corner_radius=6,
            width=60,
            height=22,
        ).pack(side="left")

        # Create Content button
        ctk.CTkButton(
            inner,
            text="Create Content",
            width=110,
            height=28,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            command=lambda kw=trend["keyword"]: self._on_create_content(kw),
        ).pack(side="right")

    def _on_create_content(self, keyword):
        """Placeholder for content-creation workflow triggered by a trend."""
        pass

    # ── Alert History ─────────────────────────────────────────────

    def _build_alert_history(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Alert History",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=14, pady=(12, 6))

        self._history_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self._history_frame.pack(fill="x", padx=10, pady=(0, 12))

        self._load_alert_history()

    def _load_alert_history(self):
        for widget in self._history_frame.winfo_children():
            widget.destroy()

        trend_types = {key for key, _ in _ALERT_TYPES}
        try:
            notifications = self.db.get_notifications(limit=30)
        except Exception:
            notifications = []

        alerts = [n for n in notifications if n.get("type") in trend_types]

        if not alerts:
            ctk.CTkLabel(
                self._history_frame,
                text="No trend alerts yet.",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(anchor="w", padx=6, pady=4)
            return

        for alert in alerts[:15]:
            row = ctk.CTkFrame(self._history_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row,
                text=alert.get("title", ""),
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_primary"],
            ).pack(side="left", padx=(6, 10))

            ctk.CTkLabel(
                row,
                text=alert.get("created_at", "")[:16],
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(side="right", padx=6)

    # ── Refresh ───────────────────────────────────────────────────

    def refresh(self):
        """Reload trends display and alert history."""
        self._populate_trends(_SAMPLE_TRENDS)
        self._load_alert_history()
