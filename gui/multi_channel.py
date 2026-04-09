# -*- coding: utf-8 -*-
"""
RealE Tube - Multi-Channel Management Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

from database.db import DatabaseManager
from gui.tooltip import under_construction_badge


class MultiChannelTab:
    """Manage multiple YouTube channels from a single interface.

    Channels are persisted in the database.  Per-channel video stats are
    shown as a placeholder because the videos table does not yet carry a
    channel_id foreign key.
    """

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self._channels_tree = None
        self._switcher_var = ctk.StringVar(value="-- select channel --")

        self.create_tab()

    # ── Main layout ───────────────────────────────────────────────

    def create_tab(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_channel_switcher(scroll)
        self._create_add_form(scroll)
        self._create_channels_list(scroll)
        self._create_action_buttons(scroll)
        self._create_per_channel_stats(scroll)

        self.refresh_channels()

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            bar,
            text="Multi-Channel Management",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        ).pack(side="left")

        badge = under_construction_badge(
            bar, self.theme,
            text="Multi-channel features are partially implemented. "
                 "Per-channel video stats require a schema migration.",
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
            command=self.refresh_channels,
        ).pack(side="right")

    # ── Channel switcher ──────────────────────────────────────────

    def _create_channel_switcher(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Active Channel",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(
            row, text="Switch to:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left", padx=(0, 8))

        self._switcher_combo = ctk.CTkComboBox(
            row,
            variable=self._switcher_var,
            values=["-- select channel --"],
            width=320,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            state="readonly",
            command=self._on_channel_switch,
        )
        self._switcher_combo.pack(side="left")

    # ── Add channel form ──────────────────────────────────────────

    def _create_add_form(self, parent):
        form = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        form.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            form, text="Add Channel",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 8))

        # Channel ID
        ctk.CTkLabel(
            row, text="Channel ID:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left", padx=(0, 4))

        self._add_id_entry = ctk.CTkEntry(
            row, width=200, height=32,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            placeholder_text="UCxxxxxxxxxxxxxxxx",
        )
        self._add_id_entry.pack(side="left", padx=(0, 12))

        # Channel name
        ctk.CTkLabel(
            row, text="Name:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left", padx=(0, 4))

        self._add_name_entry = ctk.CTkEntry(
            row, width=180, height=32,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            placeholder_text="My Channel",
        )
        self._add_name_entry.pack(side="left", padx=(0, 12))

        # Set as Default checkbox
        self._default_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            row, text="Set as Default",
            variable=self._default_var,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left", padx=(0, 12))

        # Add button
        ctk.CTkButton(
            row,
            text="Add Channel",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["success"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=120, height=32, corner_radius=8,
            command=self._on_add_channel,
        ).pack(side="left")

        # Bottom padding
        ctk.CTkFrame(form, fg_color="transparent", height=8).pack()

    # ── Channels list ─────────────────────────────────────────────

    def _create_channels_list(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            frame, text="Your Channels",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        cols = ("name", "channel_id", "default", "added")
        self._channels_tree = ttk.Treeview(
            frame, columns=cols, show="headings", height=6, selectmode="browse",
        )
        self._channels_tree.heading("name", text="Name")
        self._channels_tree.heading("channel_id", text="Channel ID")
        self._channels_tree.heading("default", text="Default")
        self._channels_tree.heading("added", text="Added")

        self._channels_tree.column("name", width=200)
        self._channels_tree.column("channel_id", width=220)
        self._channels_tree.column("default", width=80, anchor="center")
        self._channels_tree.column("added", width=160, anchor="center")

        self._channels_tree.pack(fill="x", padx=16, pady=(0, 16))

    # ── Action buttons ────────────────────────────────────────────

    def _create_action_buttons(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 16))

        ctk.CTkButton(
            row,
            text="Remove Channel",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["error"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            width=150, height=32, corner_radius=8,
            command=self._on_remove_channel,
        ).pack(side="left", padx=(0, 8))

    # ── Per-channel stats summary ─────────────────────────────────

    def _create_per_channel_stats(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame, text="Per-Channel Video Stats",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self._stats_label = ctk.CTkLabel(
            frame,
            text="Loading...",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            wraplength=700, justify="left",
        )
        self._stats_label.pack(anchor="w", padx=16, pady=(0, 8))

        self._stats_note = ctk.CTkLabel(
            frame,
            text=(
                "Note: The videos table does not yet have a channel_id foreign key. "
                "Per-channel breakdowns will become available after a schema migration "
                "links videos to their respective channels."
            ),
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
            wraplength=700, justify="left",
        )
        self._stats_note.pack(anchor="w", padx=16, pady=(0, 16))

    # ── Data operations ───────────────────────────────────────────

    def refresh_channels(self):
        """Reload everything from the database."""
        try:
            channels = self.db.get_all_channels()
        except Exception:
            channels = []

        # ---- Treeview ----
        tree = self._channels_tree
        if tree is not None:
            for item in tree.get_children():
                tree.delete(item)
            for ch in channels:
                tree.insert(
                    "", "end",
                    iid=str(ch["channel_id"]),
                    values=(
                        ch.get("channel_name", ""),
                        ch.get("channel_id", ""),
                        "Yes" if ch.get("is_default") else "No",
                        ch.get("created_at", ""),
                    ),
                )

        # ---- Switcher dropdown ----
        display_values = [
            f"{ch.get('channel_name', '')}  ({ch.get('channel_id', '')})"
            for ch in channels
        ]
        if not display_values:
            display_values = ["-- no channels --"]
        self._switcher_combo.configure(values=display_values)

        # Pre-select the default channel if one exists
        for ch in channels:
            if ch.get("is_default"):
                label = f"{ch.get('channel_name', '')}  ({ch.get('channel_id', '')})"
                self._switcher_var.set(label)
                break
        else:
            self._switcher_var.set(display_values[0])

        # ---- Per-channel stats ----
        self._update_stats(channels)

    def _update_stats(self, channels):
        """Update the per-channel stats placeholder."""
        try:
            total_videos = len(self.db.get_all_videos())
        except Exception:
            total_videos = 0

        if not channels:
            self._stats_label.configure(
                text="No channels registered yet. Add a channel above to get started."
            )
            return

        lines = [f"Registered channels: {len(channels)}"]
        lines.append(f"Total videos in database (all channels): {total_videos}")
        for ch in channels:
            name = ch.get("channel_name", "Unknown")
            default_tag = "  [DEFAULT]" if ch.get("is_default") else ""
            lines.append(
                f"\u2022 {name}{default_tag} -- video count: N/A (requires schema migration)"
            )

        self._stats_label.configure(text="\n".join(lines))

    # ── Event handlers ────────────────────────────────────────────

    def _on_add_channel(self):
        channel_id = self._add_id_entry.get().strip()
        channel_name = self._add_name_entry.get().strip()

        if not channel_id:
            messagebox.showwarning("Missing Field", "Please enter a Channel ID.")
            return
        if not channel_name:
            messagebox.showwarning("Missing Field", "Please enter a Channel Name.")
            return

        is_default = 1 if self._default_var.get() else 0

        # If setting as default, clear existing defaults first
        if is_default:
            try:
                existing = self.db.get_all_channels()
                for ch in existing:
                    if ch.get("is_default"):
                        conn = self.db.get_connection()
                        conn.execute(
                            "UPDATE channels SET is_default = 0 WHERE channel_id = ?",
                            (ch["channel_id"],),
                        )
                        conn.commit()
                        conn.close()
            except Exception:
                pass

        try:
            self.db.add_channel(channel_id, channel_name, is_default)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not add channel:\n{exc}")
            return

        self._add_id_entry.delete(0, "end")
        self._add_name_entry.delete(0, "end")
        self._default_var.set(False)
        self.refresh_channels()

    def _on_remove_channel(self):
        tree = self._channels_tree
        if tree is None:
            return
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Select a channel to remove first.")
            return

        channel_id = selection[0]
        # Retrieve channel name for the confirmation message
        channel_name = channel_id
        try:
            channels = self.db.get_all_channels()
            for ch in channels:
                if ch.get("channel_id") == channel_id:
                    channel_name = ch.get("channel_name", channel_id)
                    break
        except Exception:
            pass

        confirmed = messagebox.askyesno(
            "Confirm Removal",
            f"Remove channel '{channel_name}' ({channel_id})?\n\n"
            "This will not delete any videos from the database.",
        )
        if confirmed:
            try:
                self.db.delete_channel(channel_id)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not remove channel:\n{exc}")
                return
            self.refresh_channels()

    def _on_channel_switch(self, selection):
        """Handle channel switcher dropdown change."""
        # Extract channel_id from the display string "Name  (UCxxx)"
        if "(" in selection and selection.endswith(")"):
            channel_id = selection.rsplit("(", 1)[-1].rstrip(")")
        else:
            return

        # Update the app-level active channel reference if available
        if hasattr(self.app, "active_channel_id"):
            self.app.active_channel_id = channel_id
