"""
RealE Tube - Audience Retention Heatmap Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager

# Sample retention data (percentage retained at each segment)
_SAMPLE_RETENTION = [
    ("0-10%", 100),
    ("10-20%", 82),
    ("20-30%", 71),
    ("30-40%", 63),
    ("40-50%", 58),
    ("50-60%", 52),
    ("60-70%", 44),
    ("70-80%", 39),
    ("80-90%", 35),
    ("90-100%", 31),
]

# Thresholds for retention level colouring
_HIGH_THRESHOLD = 60
_MEDIUM_THRESHOLD = 40


def _retention_color(pct):
    """Return a hex colour for the retention percentage."""
    if pct >= _HIGH_THRESHOLD:
        return "#43A047"  # green
    if pct >= _MEDIUM_THRESHOLD:
        return "#FB8C00"  # yellow/orange
    return "#E53935"  # red


def _retention_bar(pct, width=20):
    """Return a text bar like '████████░░░░░░░░░░░░ 58%'."""
    filled = max(1, int(round(pct / 100 * width)))
    empty = width - filled
    return "\u2588" * filled + "\u2591" * empty


class RetentionHeatmapTab:
    """GUI tab for audience retention heatmap visualisation."""

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self.videos = []
        self.video_map = {}
        self._segment_labels = []

        self._build_layout()
        self._load_videos()

    # ── Layout ────────────────────────────────────────────────────

    def _build_layout(self):
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_header(main)

        scroll = ctk.CTkScrollableFrame(main, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._build_video_selector(scroll)
        self._build_overview_cards(scroll)
        self._build_heatmap(scroll)
        self._build_insights(scroll)
        self._build_footer_note(scroll)

    # ── Header ────────────────────────────────────────────────────

    def _build_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            bar,
            text="Audience Retention Analysis",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        ).pack(side="left")

        badge = under_construction_badge(bar, self.theme)
        badge.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            bar,
            text="Refresh",
            width=90,
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            command=self._on_refresh,
        ).pack(side="right")

    # ── Video Selector ────────────────────────────────────────────

    def _build_video_selector(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Select Video",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self._video_var = ctk.StringVar(value="No videos loaded")
        self._video_dropdown = ctk.CTkOptionMenu(
            frame,
            variable=self._video_var,
            values=["No videos loaded"],
            fg_color=self.theme["bg_tertiary"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            command=self._on_video_selected,
            width=400,
        )
        self._video_dropdown.pack(anchor="w", padx=12, pady=(0, 10))

    # ── Overview Cards ────────────────────────────────────────────

    def _build_overview_cards(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 12))
        row.columnconfigure((0, 1, 2), weight=1)

        cards = [
            ("Average Retention", "0%"),
            ("Average View Duration", "0:00"),
            ("Drop-off Point", "N/A"),
        ]
        self._card_values = []
        for idx, (title, default) in enumerate(cards):
            card = ctk.CTkFrame(row, fg_color=self.theme["bg_secondary"], corner_radius=8)
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 6, 0))

            ctk.CTkLabel(
                card,
                text=title,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"],
            ).pack(anchor="w", padx=12, pady=(10, 2))

            val_label = ctk.CTkLabel(
                card,
                text=default,
                font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
                text_color=self.theme["accent"],
            )
            val_label.pack(anchor="w", padx=12, pady=(0, 10))
            self._card_values.append(val_label)

    # ── Retention Heatmap ─────────────────────────────────────────

    def _build_heatmap(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Retention Heatmap  (sample data)",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self._heatmap_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self._heatmap_frame.pack(fill="x", padx=12, pady=(0, 10))

        self._render_heatmap(_SAMPLE_RETENTION)

    def _render_heatmap(self, data):
        """Draw text-based retention bars for each segment."""
        for widget in self._heatmap_frame.winfo_children():
            widget.destroy()
        self._segment_labels = []

        for segment, pct in data:
            row = ctk.CTkFrame(self._heatmap_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(
                row,
                text=segment,
                width=70,
                anchor="e",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"],
            ).pack(side="left", padx=(0, 8))

            bar_text = _retention_bar(pct)
            color = _retention_color(pct)

            bar_label = ctk.CTkLabel(
                row,
                text=bar_text,
                font=("Courier", self.theme["font_size_body"]),
                text_color=color,
                anchor="w",
            )
            bar_label.pack(side="left")

            pct_label = ctk.CTkLabel(
                row,
                text=f"  {pct}%",
                font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                text_color=color,
            )
            pct_label.pack(side="left")
            self._segment_labels.append((bar_label, pct_label))

    # ── Key Insights ──────────────────────────────────────────────

    def _build_insights(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Key Insights",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self._insights_box = ctk.CTkTextbox(
            frame,
            height=140,
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            wrap="word",
        )
        self._insights_box.pack(fill="x", padx=12, pady=(0, 10))

        default_insights = (
            "Top drop-off points:\n"
            "  - Largest audience loss between 60-70% of the video (8% drop)\n"
            "  - Early exit spike around 10-20% mark\n\n"
            "Best performing segments:\n"
            "  - Intro (0-10%) retains 100% of viewers\n"
            "  - 40-50% segment holds steady at 58%\n\n"
            "Recommendations:\n"
            "  - Add a hook or pattern interrupt near the 60% mark\n"
            "  - Consider shortening the intro to reduce early exits\n"
            "  - Place key content before the 50% mark for maximum reach"
        )
        self._insights_box.insert("1.0", default_insights)
        self._insights_box.configure(state="disabled")

    # ── Footer Note ───────────────────────────────────────────────

    def _build_footer_note(self, parent):
        ctk.CTkLabel(
            parent,
            text="Connect YouTube Analytics API in Settings to enable retention analysis",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        ).pack(anchor="w", pady=(4, 0))

    # ── Data helpers ──────────────────────────────────────────────

    def _load_videos(self):
        """Populate the video dropdown from the database."""
        try:
            self.videos = self.db.get_all_videos() or []
        except Exception:
            self.videos = []

        self.video_map = {}
        titles = []
        for v in self.videos:
            title = v.get("title", v.get("video_id", "Untitled"))
            self.video_map[title] = v
            titles.append(title)

        if titles:
            self._video_dropdown.configure(values=titles)
            self._video_var.set(titles[0])
        else:
            self._video_dropdown.configure(values=["No videos loaded"])
            self._video_var.set("No videos loaded")

    def _on_video_selected(self, choice):
        """Handle video selection (placeholder until API connected)."""
        # Retention data will come from YouTube Analytics API once connected.
        self._render_heatmap(_SAMPLE_RETENTION)

    def _on_refresh(self):
        """Reload video list and reset display."""
        self._load_videos()
        self._render_heatmap(_SAMPLE_RETENTION)
