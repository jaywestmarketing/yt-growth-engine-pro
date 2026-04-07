"""
RealE Tube - Cross-Platform Publishing Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk

from gui.tooltip import under_construction_badge


class CrossPlatformTab:
    """GUI tab for managing cross-platform content publishing."""

    # Platform definitions: name, icon, description, metadata constraints
    PLATFORMS = [
        {
            "name": "YouTube",
            "icon": "\u25b6",
            "desc": "Full-length & Shorts",
            "meta": "Full description, 500-char tags",
        },
        {
            "name": "TikTok",
            "icon": "\u266b",
            "desc": "Short-form vertical",
            "meta": "150-char caption, hashtags",
        },
        {
            "name": "Instagram Reels",
            "icon": "\u25cb",
            "desc": "Reels & Stories",
            "meta": "2,200-char caption, 30 hashtags",
        },
        {
            "name": "X / Twitter",
            "icon": "\u2715",
            "desc": "Clips & announcements",
            "meta": "280 chars, 1 link",
        },
    ]

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.create_layout()

    # ── Layout ────────────────────────────────────────────────────

    def create_layout(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_platform_cards(scroll)
        self._create_workflow_section(scroll)
        self._create_platform_settings(scroll)
        self._create_publish_section(scroll)
        self._create_status_note(scroll)

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="Cross-Platform Publishing",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(side="left")

        badge = under_construction_badge(bar, self.theme)
        badge.pack(side="left", padx=(8, 0))

    # ── Platform Connection Cards ─────────────────────────────────

    def _create_platform_cards(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 16))

        label = ctk.CTkLabel(
            section,
            text="Platform Connections",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        label.pack(anchor="w", pady=(0, 8))

        grid = ctk.CTkFrame(section, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1), weight=1)

        for idx, platform in enumerate(self.PLATFORMS):
            row, col = divmod(idx, 2)
            self._build_card(grid, platform).grid(
                row=row, column=col, padx=6, pady=6, sticky="nsew"
            )

    def _build_card(self, parent, platform):
        card = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)

        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=platform["icon"],
            font=(self.theme["font_family"], 28),
            text_color=self.theme["accent"],
        )
        icon_label.pack(pady=(14, 4))

        # Platform name
        name_label = ctk.CTkLabel(
            card,
            text=platform["name"],
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        )
        name_label.pack()

        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=platform["desc"],
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        )
        desc_label.pack()

        # Status
        status_label = ctk.CTkLabel(
            card,
            text="Not Connected",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["error"],
        )
        status_label.pack(pady=(6, 0))

        # Connect button row (button + badge)
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(6, 14))

        btn = ctk.CTkButton(
            btn_row,
            text="Connect",
            width=100,
            height=28,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            state="disabled",
        )
        btn.pack(side="left")

        badge = under_construction_badge(
            btn_row, self.theme, text=f"{platform['name']} API connection coming soon"
        )
        badge.pack(side="left", padx=(6, 0))

        return card

    # ── Publishing Workflow ────────────────────────────────────────

    def _create_workflow_section(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16), padx=0)

        title = ctk.CTkLabel(
            frame,
            text="Publishing Workflow",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(anchor="w", padx=16, pady=(14, 4))

        desc = ctk.CTkLabel(
            frame,
            text=(
                "Content can be auto-adapted and published to multiple platforms simultaneously. "
                "Each platform receives an optimised version of your video with tailored metadata, "
                "aspect ratio adjustments, and platform-specific captions. Connect your accounts "
                "above to enable one-click multi-platform publishing."
            ),
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
            wraplength=620,
            justify="left",
            anchor="w",
        )
        desc.pack(anchor="w", padx=16, pady=(0, 14))

    # ── Platform-Specific Settings ────────────────────────────────

    def _create_platform_settings(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        title = ctk.CTkLabel(
            frame,
            text="Platform Metadata Limits",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(anchor="w", padx=16, pady=(14, 8))

        for platform in self.PLATFORMS:
            row = ctk.CTkFrame(frame, fg_color=self.theme["bg_tertiary"], corner_radius=6)
            row.pack(fill="x", padx=16, pady=3)

            name_lbl = ctk.CTkLabel(
                row,
                text=f"{platform['icon']}  {platform['name']}",
                font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                text_color=self.theme["text_primary"],
                width=160,
                anchor="w",
            )
            name_lbl.pack(side="left", padx=(10, 4), pady=8)

            meta_lbl = ctk.CTkLabel(
                row,
                text=platform["meta"],
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"],
                anchor="w",
            )
            meta_lbl.pack(side="left", padx=(0, 10), pady=8)

        # Bottom padding
        spacer = ctk.CTkFrame(frame, fg_color="transparent", height=10)
        spacer.pack()

    # ── Publish To All ────────────────────────────────────────────

    def _create_publish_section(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 16))

        btn = ctk.CTkButton(
            row,
            text="Publish to All Platforms",
            width=220,
            height=36,
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            state="disabled",
        )
        btn.pack(side="left")

        badge = under_construction_badge(
            row, self.theme, text="Multi-platform publishing requires API connections"
        )
        badge.pack(side="left", padx=(8, 0))

    # ── Status Note ───────────────────────────────────────────────

    def _create_status_note(self, parent):
        note = ctk.CTkLabel(
            parent,
            text=(
                "Platform API connections coming soon. "
                "Configure each platform\u2019s credentials in Settings."
            ),
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
            anchor="w",
        )
        note.pack(anchor="w", pady=(0, 10))
