"""
RealE Tube - Competitor Channel Tracking Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import csv
import io
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog

from gui.tooltip import under_construction_badge
from database.db import DatabaseManager


class CompetitorTrackingTab:
    """GUI tab for tracking competitor YouTube channels and their videos."""

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        self._selected_channel_id = None
        self._channels_tree = None
        self._videos_tree = None
        self._summary_label = None

        self.create_layout()

    # ── Helpers ────────────────────────────────────────────────────

    def _safe_int(self, value, default=0):
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    def _format_number(self, n):
        """Return a human-friendly number string (e.g. 1,234)."""
        return f"{self._safe_int(n):,}"

    # ── Layout ────────────────────────────────────────────────────

    def create_layout(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_add_form(scroll)
        self._create_channels_tree(scroll)
        self._create_action_buttons(scroll)
        self._create_videos_tree(scroll)
        self._create_summary(scroll)

        self.refresh_channels()

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="Competitor Tracking",
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
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=100,
            height=32,
            corner_radius=8,
            command=self.refresh_channels,
        )
        btn.pack(side="right")

    # ── Add Competitor Form ───────────────────────────────────────

    def _create_add_form(self, parent):
        form_frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        form_frame.pack(fill="x", pady=(0, 15))

        form_label = ctk.CTkLabel(
            form_frame,
            text="Add Competitor Channel",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        )
        form_label.pack(anchor="w", padx=15, pady=(12, 6))

        row = ctk.CTkFrame(form_frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(0, 12))

        # Channel ID entry
        id_label = ctk.CTkLabel(
            row,
            text="Channel ID:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        )
        id_label.pack(side="left", padx=(0, 4))

        self._channel_id_entry = ctk.CTkEntry(
            row,
            width=200,
            height=32,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            placeholder_text="UCxxxxxxxxxxxxxxxx",
        )
        self._channel_id_entry.pack(side="left", padx=(0, 12))

        # Channel name entry
        name_label = ctk.CTkLabel(
            row,
            text="Name:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        )
        name_label.pack(side="left", padx=(0, 4))

        self._channel_name_entry = ctk.CTkEntry(
            row,
            width=180,
            height=32,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            placeholder_text="Channel name",
        )
        self._channel_name_entry.pack(side="left", padx=(0, 12))

        add_btn = ctk.CTkButton(
            row,
            text="Add Channel",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["success"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=120,
            height=32,
            corner_radius=8,
            command=self._on_add_channel,
        )
        add_btn.pack(side="left")

    # ── Channels Treeview ─────────────────────────────────────────

    def _create_channels_tree(self, parent):
        frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 10))

        header = ctk.CTkLabel(
            frame,
            text="Tracked Channels",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        )
        header.pack(anchor="w", padx=15, pady=(12, 6))

        cols = ("name", "channel_id", "subscribers", "videos", "last_video")
        self._channels_tree = ttk.Treeview(
            frame, columns=cols, show="headings", height=6, selectmode="browse"
        )
        self._channels_tree.heading("name", text="Name")
        self._channels_tree.heading("channel_id", text="Channel ID")
        self._channels_tree.heading("subscribers", text="Subscribers")
        self._channels_tree.heading("videos", text="Videos")
        self._channels_tree.heading("last_video", text="Last Video Date")

        self._channels_tree.column("name", width=180)
        self._channels_tree.column("channel_id", width=200)
        self._channels_tree.column("subscribers", width=100, anchor="e")
        self._channels_tree.column("videos", width=80, anchor="e")
        self._channels_tree.column("last_video", width=130, anchor="center")

        self._channels_tree.pack(fill="x", padx=15, pady=(0, 12))
        self._channels_tree.bind("<<TreeviewSelect>>", self._on_channel_select)

    # ── Action Buttons ────────────────────────────────────────────

    def _create_action_buttons(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        remove_btn = ctk.CTkButton(
            row,
            text="Remove Channel",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["error"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            width=140,
            height=32,
            corner_radius=8,
            command=self._on_remove_channel,
        )
        remove_btn.pack(side="left", padx=(0, 8))

        # Fetch Latest — needs YouTube API, so mark under-construction
        fetch_frame = ctk.CTkFrame(row, fg_color="transparent")
        fetch_frame.pack(side="left", padx=(0, 8))

        fetch_btn = ctk.CTkButton(
            fetch_frame,
            text="Fetch Latest",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            width=120,
            height=32,
            corner_radius=8,
            command=lambda: messagebox.showinfo(
                "Coming Soon",
                "Fetch Latest requires a YouTube Data API key. "
                "This feature is under construction.",
            ),
        )
        fetch_btn.pack(side="left")

        fetch_badge = under_construction_badge(fetch_frame, self.theme)
        fetch_badge.pack(side="left", padx=(4, 0))

        export_btn = ctk.CTkButton(
            row,
            text="Export Data",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=120,
            height=32,
            corner_radius=8,
            command=self._on_export,
        )
        export_btn.pack(side="left")

    # ── Videos Treeview ───────────────────────────────────────────

    def _create_videos_tree(self, parent):
        frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 10))

        header = ctk.CTkLabel(
            frame,
            text="Competitor Videos",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        )
        header.pack(anchor="w", padx=15, pady=(12, 6))

        cols = ("title", "views", "likes", "comments", "published")
        self._videos_tree = ttk.Treeview(
            frame, columns=cols, show="headings", height=8, selectmode="browse"
        )
        self._videos_tree.heading("title", text="Title")
        self._videos_tree.heading("views", text="Views")
        self._videos_tree.heading("likes", text="Likes")
        self._videos_tree.heading("comments", text="Comments")
        self._videos_tree.heading("published", text="Published")

        self._videos_tree.column("title", width=300)
        self._videos_tree.column("views", width=90, anchor="e")
        self._videos_tree.column("likes", width=80, anchor="e")
        self._videos_tree.column("comments", width=90, anchor="e")
        self._videos_tree.column("published", width=130, anchor="center")

        self._videos_tree.pack(fill="x", padx=15, pady=(0, 12))

    # ── Summary ───────────────────────────────────────────────────

    def _create_summary(self, parent):
        frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_tertiary"], corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 10))

        self._summary_label = ctk.CTkLabel(
            frame,
            text="",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
            anchor="w",
        )
        self._summary_label.pack(padx=15, pady=10, anchor="w")

        self._update_summary()

    # ── Data Operations ───────────────────────────────────────────

    def refresh_channels(self):
        """Reload the channels treeview and summary from the database."""
        tree = self._channels_tree
        if tree is None:
            return
        for item in tree.get_children():
            tree.delete(item)

        channels = self.db.get_all_competitor_channels()
        for ch in channels:
            tree.insert(
                "",
                "end",
                iid=str(ch["channel_id"]),
                values=(
                    ch.get("channel_name", ""),
                    ch.get("channel_id", ""),
                    self._format_number(ch.get("subscriber_count")),
                    self._format_number(ch.get("video_count")),
                    ch.get("last_video_date", "—") or "—",
                ),
            )

        # Clear videos pane
        self._clear_videos()
        self._selected_channel_id = None
        self._update_summary()

    def _clear_videos(self):
        if self._videos_tree is None:
            return
        for item in self._videos_tree.get_children():
            self._videos_tree.delete(item)

    def _load_videos(self, competitor_db_id):
        """Populate the videos treeview for the given competitor channel DB id."""
        self._clear_videos()
        videos = self.db.get_competitor_videos(competitor_db_id)
        for v in videos:
            self._videos_tree.insert(
                "",
                "end",
                values=(
                    v.get("title", ""),
                    self._format_number(v.get("views")),
                    self._format_number(v.get("likes")),
                    self._format_number(v.get("comments")),
                    v.get("published_at", "—") or "—",
                ),
            )

    def _update_summary(self):
        if self._summary_label is None:
            return
        channels = self.db.get_all_competitor_channels()
        total = len(channels)
        if total > 0:
            avg_subs = sum(self._safe_int(c.get("subscriber_count")) for c in channels) // total
        else:
            avg_subs = 0
        self._summary_label.configure(
            text=f"Total competitors tracked: {total}   |   "
                 f"Avg subscriber count: {self._format_number(avg_subs)}"
        )

    # ── Event Handlers ────────────────────────────────────────────

    def _on_add_channel(self):
        channel_id = self._channel_id_entry.get().strip()
        channel_name = self._channel_name_entry.get().strip()

        if not channel_id:
            messagebox.showwarning("Missing Field", "Please enter a Channel ID.")
            return
        if not channel_name:
            messagebox.showwarning("Missing Field", "Please enter a Channel Name.")
            return

        self.db.add_competitor_channel(channel_id, channel_name)
        self._channel_id_entry.delete(0, "end")
        self._channel_name_entry.delete(0, "end")
        self.refresh_channels()

    def _on_channel_select(self, _event=None):
        selection = self._channels_tree.selection()
        if not selection:
            return
        channel_id = selection[0]
        self._selected_channel_id = channel_id

        # Look up the internal DB id for this channel
        channels = self.db.get_all_competitor_channels()
        db_id = None
        for ch in channels:
            if ch.get("channel_id") == channel_id:
                db_id = ch.get("id")
                break
        if db_id is not None:
            self._load_videos(db_id)

    def _on_remove_channel(self):
        if not self._selected_channel_id:
            messagebox.showinfo("No Selection", "Select a channel to remove first.")
            return
        confirmed = messagebox.askyesno(
            "Confirm Removal",
            f"Remove channel '{self._selected_channel_id}' and all its tracked videos?",
        )
        if confirmed:
            self.db.delete_competitor_channel(self._selected_channel_id)
            self.refresh_channels()

    def _on_export(self):
        """Export all competitor channels and their videos to a CSV file."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Competitor Data",
        )
        if not path:
            return

        channels = self.db.get_all_competitor_channels()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Channel Name", "Channel ID", "Subscribers", "Videos",
                "Last Video Date", "Video Title", "Views", "Likes",
                "Comments", "Published",
            ])
            for ch in channels:
                videos = self.db.get_competitor_videos(ch["id"])
                if videos:
                    for v in videos:
                        writer.writerow([
                            ch.get("channel_name", ""),
                            ch.get("channel_id", ""),
                            ch.get("subscriber_count", 0),
                            ch.get("video_count", 0),
                            ch.get("last_video_date", ""),
                            v.get("title", ""),
                            v.get("views", 0),
                            v.get("likes", 0),
                            v.get("comments", 0),
                            v.get("published_at", ""),
                        ])
                else:
                    writer.writerow([
                        ch.get("channel_name", ""),
                        ch.get("channel_id", ""),
                        ch.get("subscriber_count", 0),
                        ch.get("video_count", 0),
                        ch.get("last_video_date", ""),
                        "", "", "", "", "",
                    ])

        messagebox.showinfo("Export Complete", f"Data exported to:\n{path}")
