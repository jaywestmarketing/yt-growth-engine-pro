"""
RealE Tube - Multi-Channel Management Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager


class MultiChannelTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self._create_ui()

    def _create_ui(self):
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        t = self.theme

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header, text="Multi-Channel Management",
            font=(t["font_family"], t["font_size_heading"], "bold"),
            text_color=t["text_primary"]
        ).pack(side="left", padx=20, pady=15)

        badge = under_construction_badge(header, t)
        badge.pack(side="left", pady=15)

        ctk.CTkButton(
            header, text="↻ Refresh", width=100, height=32,
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"], hover_color=t["accent_hover"],
            text_color="#FFFFFF", corner_radius=8,
            command=self.refresh
        ).pack(side="right", padx=20, pady=15)

        # ── Active channel selector ──────────────────────────────
        selector_frame = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        selector_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            selector_frame, text="Active Channel:",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"]
        ).pack(side="left", padx=20, pady=12)

        self.channel_selector = ctk.CTkOptionMenu(
            selector_frame, values=["(no channels)"],
            fg_color=t["button_bg"], button_color=t["accent"],
            button_hover_color=t["accent_hover"],
            text_color=t["text_primary"],
            font=(t["font_family"], t["font_size_body"]), width=300
        )
        self.channel_selector.pack(side="left", padx=10, pady=12)

        # ── Add channel form ─────────────────────────────────────
        form_frame = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            form_frame, text="Add Channel",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        row = ctk.CTkFrame(form_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(row, text="Channel ID:", width=90, anchor="w",
                     font=(t["font_family"], t["font_size_small"]),
                     text_color=t["text_secondary"]).pack(side="left")
        self.channel_id_entry = ctk.CTkEntry(
            row, width=220, placeholder_text="UC...",
            fg_color=t["bg_tertiary"], text_color=t["text_primary"],
            font=(t["font_family"], t["font_size_body"])
        )
        self.channel_id_entry.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row, text="Name:", width=50, anchor="w",
                     font=(t["font_family"], t["font_size_small"]),
                     text_color=t["text_secondary"]).pack(side="left")
        self.channel_name_entry = ctk.CTkEntry(
            row, width=200, placeholder_text="My Channel",
            fg_color=t["bg_tertiary"], text_color=t["text_primary"],
            font=(t["font_family"], t["font_size_body"])
        )
        self.channel_name_entry.pack(side="left", padx=(0, 15))

        self.default_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            row, text="Default", variable=self.default_var,
            font=(t["font_family"], t["font_size_small"]),
            text_color=t["text_secondary"]
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            row, text="Add Channel", width=120, height=32,
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"], hover_color=t["accent_hover"],
            text_color="#FFFFFF", corner_radius=8,
            command=self._add_channel
        ).pack(side="left")

        # ── Channels table ───────────────────────────────────────
        table_frame = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 15))

        ctk.CTkLabel(
            table_frame, text="Registered Channels",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        style = ttk.Style()
        style.configure("MC.Treeview", background=t["bg_tertiary"],
                        foreground=t["text_primary"], fieldbackground=t["bg_tertiary"],
                        borderwidth=0, font=(t["font_family"], 12))
        style.configure("MC.Treeview.Heading", background=t["bg_secondary"],
                        foreground=t["text_primary"], borderwidth=0,
                        font=(t["font_family"], 12, "bold"))

        cols = ("Name", "Channel ID", "Default")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                 style="MC.Treeview", height=6)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.column("Name", width=250)
        self.tree.column("Channel ID", width=280)
        self.tree.column("Default", width=80)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # ── Actions ──────────────────────────────────────────────
        actions = ctk.CTkFrame(main, fg_color="transparent")
        actions.pack(fill="x")

        ctk.CTkButton(
            actions, text="Remove Channel", height=40,
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["error"], hover_color=t["error"],
            text_color="#FFFFFF", corner_radius=8,
            command=self._remove_channel
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            actions,
            text="Note: videos table does not yet have a channel_id column — per-channel stats coming soon.",
            font=(t["font_family"], t["font_size_small"]),
            text_color=t["text_tertiary"], wraplength=500, anchor="w"
        ).pack(side="left", padx=10)

        self._load_channels()

    # ── Data ─────────────────────────────────────────────────────

    def _load_channels(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            channels = self.db.get_all_channels()
            names = []
            for ch in channels:
                name = ch.get("channel_name") or ch.get("channel_id", "")
                default = "Yes" if ch.get("is_default") else ""
                self.tree.insert("", "end", values=(name, ch.get("channel_id", ""), default))
                names.append(name)
            if names:
                self.channel_selector.configure(values=names)
                self.channel_selector.set(names[0])
            else:
                self.channel_selector.configure(values=["(no channels)"])
                self.channel_selector.set("(no channels)")
        except Exception as e:
            print(f"Error loading channels: {e}")

    def _add_channel(self):
        cid = self.channel_id_entry.get().strip()
        cname = self.channel_name_entry.get().strip()
        if not cid:
            self.app.dashboard_tab.add_log_entry("Channel ID is required", "ERROR")
            return
        try:
            self.db.add_channel(cid, cname or cid, int(self.default_var.get()))
            self.channel_id_entry.delete(0, "end")
            self.channel_name_entry.delete(0, "end")
            self._load_channels()
            self.app.dashboard_tab.add_log_entry(f"Channel added: {cname or cid}", "SUCCESS")
        except Exception as e:
            self.app.dashboard_tab.add_log_entry(f"Error adding channel: {e}", "ERROR")

    def _remove_channel(self):
        sel = self.tree.selection()
        if not sel:
            self.app.dashboard_tab.add_log_entry("No channel selected", "ERROR")
            return
        vals = self.tree.item(sel[0])["values"]
        if not messagebox.askyesno("Confirm", f"Remove channel {vals[0]}?"):
            return
        try:
            self.db.delete_channel(str(vals[1]))
            self._load_channels()
            self.app.dashboard_tab.add_log_entry(f"Channel removed: {vals[0]}", "WARNING")
        except Exception as e:
            self.app.dashboard_tab.add_log_entry(f"Error removing channel: {e}", "ERROR")

    def refresh(self):
        self._load_channels()
        self.app.dashboard_tab.add_log_entry("Channels refreshed", "INFO")
