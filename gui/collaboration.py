"""
RealE Tube - Collaborative Workspaces Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk

from gui.tooltip import under_construction_badge


class CollaborationTab:
    """Collaborative Workspaces tab -- entirely under construction."""

    ROLES = ["Owner", "Editor", "Uploader", "Analyst", "Viewer"]
    ROLE_DESCRIPTIONS = {
        "Owner": "Full access. Manage members, billing, and all settings.",
        "Editor": "Edit videos, metadata, SEO settings, and scheduling.",
        "Uploader": "Upload new videos and manage their own uploads.",
        "Analyst": "View analytics dashboards and export reports.",
        "Viewer": "Read-only access to workspace content.",
    }
    PERMISSIONS = [
        "View analytics",
        "Upload videos",
        "Edit metadata",
        "Manage schedule",
        "Manage members",
        "Workspace settings",
    ]
    PERMISSION_MATRIX = {
        #                   View  Upload  Edit  Schedule  Members  Settings
        "Owner":    [True,  True,  True,  True,  True,  True],
        "Editor":   [True,  False, True,  True,  False, False],
        "Uploader": [False, True,  False, False, False, False],
        "Analyst":  [True,  False, False, False, False, False],
        "Viewer":   [True,  False, False, False, False, False],
    }
    ROADMAP_ITEMS = [
        "Real-time collaborative editing and sync",
        "Role-based access control with granular permissions",
        "Full audit log for all workspace actions",
        "Shared content calendar across team members",
    ]

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.create_tab()

    # ── Main layout ───────────────────────────────────────────────

    def create_tab(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_team_members_section(scroll)
        self._create_activity_feed(scroll)
        self._create_workspace_settings(scroll)
        self._create_status_note(scroll)
        self._create_roadmap(scroll)

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            bar,
            text="Collaborative Workspaces",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(side="left")

        badge = under_construction_badge(
            bar, self.theme,
            "Collaborative workspaces are under construction and require auth infrastructure.",
        )
        badge.pack(side="left", padx=(8, 0))

    # ── Team members ──────────────────────────────────────────────

    def _create_team_members_section(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            header,
            text="Team Members",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(side="left")

        invite_badge = under_construction_badge(header, self.theme, "Invite functionality coming soon.")
        invite_badge.pack(side="right", padx=(4, 0))

        invite_btn = ctk.CTkButton(
            header,
            text="Invite Member",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            state="disabled",
            width=120,
            height=30,
        )
        invite_btn.pack(side="right")

        # Members list placeholder
        list_frame = ctk.CTkFrame(frame, fg_color=self.theme["bg_tertiary"], corner_radius=6)
        list_frame.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(
            list_frame,
            text="Roles available in collaborative workspaces:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(anchor="w", padx=12, pady=(10, 4))

        for role in self.ROLES:
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(
                row, text=f"\u2022 {role}",
                font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                text_color=self.theme["text_primary"], width=80, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f"  {self.ROLE_DESCRIPTIONS[role]}",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(side="left")

            badge = under_construction_badge(row, self.theme, f"{role} role is not yet available.")
            badge.pack(side="right")

    # ── Activity feed ─────────────────────────────────────────────

    def _create_activity_feed(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame, text="Activity Feed",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            frame, text="Recent team activity will appear here.",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

    # ── Workspace settings ────────────────────────────────────────

    def _create_workspace_settings(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame, text="Workspace Settings",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Workspace name entry
        name_row = ctk.CTkFrame(frame, fg_color="transparent")
        name_row.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkLabel(
            name_row, text="Workspace Name:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left")
        ctk.CTkEntry(
            name_row, placeholder_text="My Workspace",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            state="disabled", width=220, height=30,
        ).pack(side="left", padx=(8, 0))

        # Permission matrix
        ctk.CTkLabel(
            frame, text="Permission Matrix",
            font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
            text_color=self.theme["text_secondary"],
        ).pack(anchor="w", padx=16, pady=(4, 4))

        grid_frame = ctk.CTkFrame(frame, fg_color=self.theme["bg_tertiary"], corner_radius=6)
        grid_frame.pack(fill="x", padx=16, pady=(0, 12))

        # Column headers
        for col_idx, perm in enumerate(self.PERMISSIONS):
            ctk.CTkLabel(
                grid_frame, text=perm,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"], width=100,
            ).grid(row=0, column=col_idx + 1, padx=4, pady=(8, 2))

        # Role rows
        for row_idx, role in enumerate(self.ROLES):
            ctk.CTkLabel(
                grid_frame, text=role,
                font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                text_color=self.theme["text_primary"], width=80, anchor="w",
            ).grid(row=row_idx + 1, column=0, padx=(12, 4), pady=2, sticky="w")
            for col_idx, has_perm in enumerate(self.PERMISSION_MATRIX[role]):
                mark = "\u2713" if has_perm else "\u2014"
                color = self.theme["success"] if has_perm else self.theme["text_tertiary"]
                ctk.CTkLabel(
                    grid_frame, text=mark,
                    font=(self.theme["font_family"], self.theme["font_size_small"]),
                    text_color=color, width=100,
                ).grid(row=row_idx + 1, column=col_idx + 1, padx=4, pady=2)

    # ── Status note ───────────────────────────────────────────────

    def _create_status_note(self, parent):
        note = ctk.CTkLabel(
            parent,
            text=(
                "Collaborative workspaces require cloud authentication infrastructure. "
                "This feature is being developed for a future release."
            ),
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["warning"],
            wraplength=700,
            justify="left",
        )
        note.pack(anchor="w", pady=(0, 12))

    # ── Feature roadmap ───────────────────────────────────────────

    def _create_roadmap(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            frame, text="Feature Roadmap",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(12, 4))

        for item in self.ROADMAP_ITEMS:
            ctk.CTkLabel(
                frame, text=f"\u2022  {item}",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"],
            ).pack(anchor="w", padx=24, pady=1)

        # Bottom padding
        ctk.CTkFrame(frame, fg_color="transparent", height=10).pack()
