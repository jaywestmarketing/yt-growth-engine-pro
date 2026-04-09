# -*- coding: utf-8 -*-
"""
RealE Tube - Revenue & CPM Analytics Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager


class RevenueAnalyticsTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self._metric_value_labels = {}
        self._revenue_table_container = None
        self._keywords_container = None
        self._trend_container = None

        self.create_revenue_analytics()

    # ── Layout ────────────────────────────────────────────────────

    def create_revenue_analytics(self):
        """Create the revenue analytics layout."""
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_metric_cards(scroll)
        self._create_revenue_table(scroll)
        self._create_revenue_by_keyword(scroll)
        self._create_monthly_trend(scroll)
        self._create_config_note(scroll)

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        """Header bar with title, under-construction badge, and refresh."""
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="Revenue & CPM Analytics",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(side="left")

        badge = under_construction_badge(
            bar, self.theme,
            text="Requires YouTube Analytics API connection",
        )
        badge.pack(side="left", padx=(8, 0))

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
            command=self.refresh_revenue,
        )
        btn.pack(side="right")

    # ── Metric cards ──────────────────────────────────────────────

    def _create_metric_cards(self, parent):
        """Top-level revenue metric cards with placeholder values."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            frame, text="Revenue Overview",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"], anchor="w",
        ).pack(fill="x", padx=20, pady=(20, 15))

        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 10))
        container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        metrics = [
            ("est_revenue", "Estimated Revenue", "$0.00", self.theme["success"]),
            ("avg_cpm", "Average CPM", "$0.00", self.theme["accent"]),
            ("avg_rpm", "Average RPM", "$0.00", self.theme["accent"]),
            ("monetized_views", "Total Monetized Views", "0", self.theme["text_primary"]),
        ]

        for col, (key, mtitle, mvalue, mcolor) in enumerate(metrics):
            card = ctk.CTkFrame(container, fg_color=self.theme["bg_tertiary"], corner_radius=8)
            card.grid(row=0, column=col, padx=8, sticky="ew")

            val_label = ctk.CTkLabel(
                card, text=mvalue,
                font=(self.theme["font_family"], 32, "bold"),
                text_color=mcolor,
            )
            val_label.pack(pady=(18, 4))
            self._metric_value_labels[key] = val_label

            ctk.CTkLabel(
                card, text=mtitle,
                font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
                text_color=self.theme["text_secondary"],
            ).pack(pady=(0, 4))

            ctk.CTkLabel(
                card, text="YouTube Analytics API required",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(pady=(0, 18))

    # ── Revenue by video table ────────────────────────────────────

    def _create_revenue_table(self, parent):
        """Placeholder table for per-video revenue breakdown."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            frame, text="Revenue by Video",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"], anchor="w",
        ).pack(fill="x", padx=20, pady=(20, 15))

        self._revenue_table_container = ctk.CTkFrame(
            frame, fg_color=self.theme["bg_tertiary"], corner_radius=8, height=120,
        )
        self._revenue_table_container.pack(fill="x", padx=20, pady=(0, 20))
        self._revenue_table_container.pack_propagate(False)

        ctk.CTkLabel(
            self._revenue_table_container,
            text=(
                "Per-video revenue data will appear here once the YouTube Analytics\n"
                "API is connected. Each row will show estimated earnings, CPM, RPM,\n"
                "and monetized playbacks for individual videos."
            ),
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_tertiary"],
            justify="center",
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ── Revenue by keyword ────────────────────────────────────────

    def _create_revenue_by_keyword(self, parent):
        """Section showing most profitable keywords."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            frame, text="Revenue by Keyword",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"], anchor="w",
        ).pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            frame,
            text="Most profitable keywords ranked by estimated revenue per 1,000 views",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"], anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 15))

        self._keywords_container = ctk.CTkFrame(
            frame, fg_color=self.theme["bg_tertiary"], corner_radius=8, height=100,
        )
        self._keywords_container.pack(fill="x", padx=20, pady=(0, 20))
        self._keywords_container.pack_propagate(False)

        ctk.CTkLabel(
            self._keywords_container,
            text="Keyword revenue data requires YouTube Analytics API connection.",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_tertiary"],
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ── Monthly revenue trend ─────────────────────────────────────

    def _create_monthly_trend(self, parent):
        """Text-based monthly revenue trend section."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            frame, text="Monthly Revenue Trend",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"], anchor="w",
        ).pack(fill="x", padx=20, pady=(20, 15))

        self._trend_container = ctk.CTkFrame(
            frame, fg_color=self.theme["bg_tertiary"], corner_radius=8, height=220,
        )
        self._trend_container.pack(fill="x", padx=20, pady=(0, 20))
        self._trend_container.pack_propagate(False)

        ctk.CTkLabel(
            self._trend_container,
            text=(
                "Monthly revenue trends will be displayed here\n\n"
                "Tracks: estimated earnings, CPM changes, RPM changes,\n"
                "and monetized view counts per month"
            ),
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_tertiary"],
            justify="center",
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ── Configuration note ────────────────────────────────────────

    def _create_config_note(self, parent):
        """Bottom note explaining how to enable revenue tracking."""
        note = ctk.CTkFrame(parent, fg_color=self.theme["bg_tertiary"], corner_radius=8)
        note.pack(fill="x")

        ctk.CTkLabel(
            note,
            text=(
                "Connect YouTube Analytics API in Settings to enable revenue tracking. "
                "Requires YouTube Partner Program membership."
            ),
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
            wraplength=700,
        ).pack(padx=20, pady=14)

    # ── Refresh ───────────────────────────────────────────────────

    def refresh_revenue(self):
        """Refresh placeholder — will populate once API is connected."""
        if hasattr(self.app, "dashboard_tab"):
            self.app.dashboard_tab.add_log_entry(
                "Revenue analytics refresh requested (API not connected)", "INFO",
            )
