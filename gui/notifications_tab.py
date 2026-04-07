"""
RealE Tube - Notifications & Alerts Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager

_TYPE_ICONS = {
    "performance": ("📊", "#2196F3"), "upload": ("✅", "#43A047"),
    "retry": ("🔄", "#FB8C00"), "milestone": ("🏆", "#FFD600"),
    "trend": ("📈", "#9C27B0"), "info": ("ℹ️", "#607D8B"),
}

_ALERT_OPTIONS = [
    ("performance", "Performance alerts"), ("upload", "Upload complete"),
    ("retry", "Retry triggered"), ("milestone", "Milestone reached"),
    ("trend", "Trend detected"),
]


class NotificationsTab:
    """GUI tab for notification and alert management."""

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()
        self._alert_vars = {}
        self._webhook_entry = None
        self._email_toggle = None
        self._notif_frame = None
        self._unread_label = None
        self._build_layout()

    # ── Layout ────────────────────────────────────────────────────

    def _build_layout(self):
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        self._build_header(main)
        scroll = ctk.CTkScrollableFrame(main, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._build_settings_panel(scroll)
        self._build_notification_center(scroll)
        self._build_action_buttons(scroll)

    # ── Header ────────────────────────────────────────────────────

    def _build_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            bar, text="Notifications & Alerts",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"], anchor="w",
        ).pack(side="left")
        self._unread_label = ctk.CTkLabel(
            bar, text="0",
            font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
            text_color="#FFFFFF", fg_color=self.theme["error"],
            corner_radius=10, width=26, height=26,
        )
        self._unread_label.pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            bar, text="↻ Refresh", width=90, height=30,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["button_bg"], hover_color=self.theme["button_hover"],
            command=self.refresh,
        ).pack(side="right")

    # ── Settings Panel ────────────────────────────────────────────

    def _build_settings_panel(self, parent):
        t = self.theme
        frame = ctk.CTkFrame(parent, fg_color=t["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            frame, text="Notification Settings",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"],
        ).pack(anchor="w", padx=14, pady=(12, 6))
        # Webhook URL
        webhook_row = ctk.CTkFrame(frame, fg_color="transparent")
        webhook_row.pack(fill="x", padx=14, pady=(0, 6))
        ctk.CTkLabel(
            webhook_row, text="Webhook URL (Discord / Slack)",
            font=(t["font_family"], t["font_size_small"]), text_color=t["text_secondary"],
        ).pack(side="left")
        under_construction_badge(webhook_row, t).pack(side="left", padx=(6, 0))
        self._webhook_entry = ctk.CTkEntry(
            frame, placeholder_text="https://hooks.slack.com/services/...",
            font=(t["font_family"], t["font_size_body"]), height=34,
        )
        self._webhook_entry.pack(fill="x", padx=14, pady=(0, 8))
        # Email toggle
        email_row = ctk.CTkFrame(frame, fg_color="transparent")
        email_row.pack(fill="x", padx=14, pady=(0, 8))
        self._email_toggle = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            email_row, text="Email notifications", variable=self._email_toggle,
            font=(t["font_family"], t["font_size_body"]), text_color=t["text_secondary"],
            fg_color=t["bg_tertiary"], progress_color=t["accent"],
        ).pack(side="left")
        under_construction_badge(email_row, t).pack(side="left", padx=(6, 0))
        # Alert type checkboxes
        ctk.CTkLabel(
            frame, text="Alert Types",
            font=(t["font_family"], t["font_size_small"]), text_color=t["text_tertiary"],
        ).pack(anchor="w", padx=14, pady=(4, 2))
        for key, label in _ALERT_OPTIONS:
            var = ctk.BooleanVar(value=True)
            self._alert_vars[key] = var
            ctk.CTkCheckBox(
                frame, text=label, variable=var,
                font=(t["font_family"], t["font_size_body"]), text_color=t["text_secondary"],
                fg_color=t["accent"], hover_color=t["accent_hover"],
            ).pack(anchor="w", padx=20, pady=3)
        ctk.CTkButton(
            frame, text="Save Settings", width=120, height=34,
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"], hover_color=t["accent_hover"],
            command=self._save_settings,
        ).pack(anchor="w", padx=14, pady=(8, 12))

    # ── Notification Center ───────────────────────────────────────

    def _build_notification_center(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            frame, text="Notification Center",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=14, pady=(12, 6))
        self._notif_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent", height=320)
        self._notif_frame.pack(fill="x", padx=10, pady=(0, 10))
        self._load_notifications()

    def _load_notifications(self):
        """Fetch notifications from the database and render cards."""
        for w in self._notif_frame.winfo_children():
            w.destroy()
        notifications = self.db.get_notifications(limit=50)
        unread = sum(1 for n in notifications if not n.get("is_read"))
        if self._unread_label:
            self._unread_label.configure(
                text=str(unread),
                fg_color=self.theme["error"] if unread else self.theme["bg_tertiary"],
            )
        if not notifications:
            ctk.CTkLabel(
                self._notif_frame, text="No notifications yet.",
                font=(self.theme["font_family"], self.theme["font_size_body"]),
                text_color=self.theme["text_tertiary"],
            ).pack(pady=20)
            return
        for notif in notifications:
            self._create_notification_card(notif)

    def _create_notification_card(self, notif):
        t = self.theme
        is_read = notif.get("is_read", False)
        bg = t["bg_tertiary"] if is_read else t["accent"] + "18"
        card = ctk.CTkFrame(self._notif_frame, fg_color=bg, corner_radius=8)
        card.pack(fill="x", pady=3)
        ntype = notif.get("type", "info")
        icon, color = _TYPE_ICONS.get(ntype, _TYPE_ICONS["info"])
        ctk.CTkLabel(
            card, text=icon, font=(t["font_family"], 18), text_color=color, width=32,
        ).pack(side="left", padx=(10, 6), pady=8)
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True, pady=6)
        ctk.CTkLabel(
            text_frame, text=notif.get("title", "Notification"),
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"], anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_frame, text=notif.get("message", ""),
            font=(t["font_family"], t["font_size_small"]),
            text_color=t["text_secondary"], anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            card, text=notif.get("created_at", "")[:16],
            font=(t["font_family"], t["font_size_small"]), text_color=t["text_tertiary"],
        ).pack(side="right", padx=10)
        if not is_read:
            nid = notif.get("id")
            card.bind("<Button-1>", lambda e, _id=nid: self._on_card_click(_id))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, _id=nid: self._on_card_click(_id))

    def _on_card_click(self, notification_id):
        self.db.mark_notification_read(notification_id)
        self._load_notifications()

    # ── Action Buttons ────────────────────────────────────────────

    def _build_action_buttons(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 12))
        ctk.CTkButton(
            row, text="Mark All Read", width=130, height=34,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["button_bg"], hover_color=self.theme["button_hover"],
            command=self._mark_all_read,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            row, text="Clear All", width=100, height=34,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["error"], hover_color=self.theme["warning"],
            command=self._clear_all,
        ).pack(side="left")

    # ── Actions ───────────────────────────────────────────────────

    def _save_settings(self):
        """Persist notification settings (placeholder)."""
        pass

    def _mark_all_read(self):
        for n in self.db.get_notifications(unread_only=True, limit=200):
            self.db.mark_notification_read(n["id"])
        self._load_notifications()

    def _clear_all(self):
        self.db.clear_notifications()
        self._load_notifications()

    def refresh(self):
        """Reload notification list from the database."""
        self._load_notifications()
