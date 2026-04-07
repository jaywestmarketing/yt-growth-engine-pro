# -*- coding: utf-8 -*-
"""
RealE Tube - Predictive Performance Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.db import DatabaseManager
from gui.tooltip import under_construction_badge


class PredictiveTab:
    """Predicts video performance based on historical keyword/metadata correlations.

    Currently under construction -- requires sufficient training data (uploaded
    videos with tracked metrics) before the ML model can produce meaningful
    predictions.
    """

    NICHE_OPTIONS = [
        "Real Estate", "Finance", "Tech", "Lifestyle",
        "Education", "Gaming", "Health", "Travel", "Other",
    ]

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self.create_tab()

    # ── Main layout ───────────────────────────────────────────────

    def create_tab(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_prediction_form(scroll)
        self._create_prediction_results(scroll)
        self._create_historical_accuracy(scroll)
        self._create_how_it_works(scroll)
        self._create_training_status(scroll)

        self._refresh_training_count()

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            bar,
            text="Predictive Performance",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        ).pack(side="left")

        badge = under_construction_badge(
            bar, self.theme,
            text="This feature is under construction. ML prediction requires training data from uploaded videos.",
        )
        badge.pack(side="left", padx=(8, 0))

    # ── Prediction form ───────────────────────────────────────────

    def _create_prediction_form(self, parent):
        form = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        form.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            form,
            text="Predict Video Performance",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Title
        self._title_var = ctk.StringVar()
        self._add_form_row(form, "Title:", self._title_var, "Enter a working title")

        # Description
        self._desc_var = ctk.StringVar()
        self._add_form_row(form, "Description:", self._desc_var, "Brief description or keywords")

        # Tags
        self._tags_var = ctk.StringVar()
        self._add_form_row(form, "Tags:", self._tags_var, "Comma-separated tags")

        # Niche dropdown
        niche_row = ctk.CTkFrame(form, fg_color="transparent")
        niche_row.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            niche_row,
            text="Niche:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            width=100, anchor="w",
        ).pack(side="left")

        self._niche_var = ctk.StringVar(value=self.NICHE_OPTIONS[0])
        ctk.CTkComboBox(
            niche_row,
            variable=self._niche_var,
            values=self.NICHE_OPTIONS,
            width=260,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            state="readonly",
        ).pack(side="left", padx=(8, 0))

        # Predict button + badge
        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(4, 16))

        ctk.CTkButton(
            btn_row,
            text="Predict Performance",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=180, height=36, corner_radius=8,
            command=self._run_prediction,
        ).pack(side="left")

        badge = under_construction_badge(
            btn_row, self.theme, text="Prediction engine not yet trained.",
        )
        badge.pack(side="left", padx=(8, 0))

    def _add_form_row(self, parent, label, var, placeholder):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            row, text=label,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            width=100, anchor="w",
        ).pack(side="left")

        ctk.CTkEntry(
            row, textvariable=var, placeholder_text=placeholder,
            width=400,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
        ).pack(side="left", padx=(8, 0))

    # ── Prediction results placeholder ────────────────────────────

    def _create_prediction_results(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame,
            text="Prediction Results",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        cards_row = ctk.CTkFrame(frame, fg_color="transparent")
        cards_row.pack(fill="x", padx=16, pady=(0, 16))

        metrics = [
            ("Predicted Views", "--", "Range estimate based on similar videos"),
            ("Predicted CTR", "--%", "Click-through rate estimate"),
            ("Predicted Engagement", "--%", "Like + comment rate estimate"),
            ("Confidence Level", "N/A", "Model certainty for this prediction"),
        ]

        self._result_labels = {}
        for title, default, tip in metrics:
            card = ctk.CTkFrame(cards_row, fg_color=self.theme["bg_tertiary"], corner_radius=8)
            card.pack(side="left", expand=True, fill="both", padx=(0, 8))

            ctk.CTkLabel(
                card, text=title,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(anchor="w", padx=12, pady=(10, 2))

            val_label = ctk.CTkLabel(
                card, text=default,
                font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
                text_color=self.theme["text_primary"],
            )
            val_label.pack(anchor="w", padx=12, pady=(0, 4))
            self._result_labels[title] = val_label

            ctk.CTkLabel(
                card, text=tip,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
                wraplength=180,
            ).pack(anchor="w", padx=12, pady=(0, 10))

    # ── Historical accuracy ───────────────────────────────────────

    def _create_historical_accuracy(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Historical Accuracy",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            frame,
            text=(
                "Model accuracy improves as more videos are uploaded. "
                "Currently: insufficient data."
            ),
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            wraplength=700, justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 16))

    # ── How it works ──────────────────────────────────────────────

    def _create_how_it_works(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="How It Works",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            frame,
            text=(
                "Uses historical keyword + metadata \u2192 performance correlations "
                "to estimate view counts before upload. The model analyses titles, "
                "descriptions, tags, and niche data from your previously uploaded "
                "videos to find patterns that correlate with higher views, CTR, "
                "and engagement."
            ),
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            wraplength=700, justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 16))

    # ── Training data status ──────────────────────────────────────

    def _create_training_status(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Training Data Status",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self._training_label = ctk.CTkLabel(
            frame,
            text="Checking database...",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            wraplength=700, justify="left",
        )
        self._training_label.pack(anchor="w", padx=16, pady=(0, 16))

    # ── Data helpers ──────────────────────────────────────────────

    def _refresh_training_count(self):
        try:
            videos = self.db.get_all_videos()
            usable = [v for v in videos if v.get("views") is not None and v.get("views", 0) > 0]
            total = len(videos)
            usable_count = len(usable)
        except Exception:
            total = 0
            usable_count = 0

        self._training_label.configure(
            text=(
                f"Total videos in database: {total}\n"
                f"Videos with tracked metrics (usable for training): {usable_count}\n\n"
                + (
                    "Minimum 20 videos with metrics are recommended before predictions "
                    "become meaningful."
                    if usable_count < 20
                    else "Sufficient data may be available. Model training coming soon."
                )
            )
        )

    def _run_prediction(self):
        messagebox.showinfo(
            "Under Construction",
            "The predictive model is not yet trained.\n\n"
            "Continue uploading and tracking videos to build the dataset "
            "needed for accurate predictions.",
        )
