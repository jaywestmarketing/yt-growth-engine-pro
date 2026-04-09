# -*- coding: utf-8 -*-
"""
RealE Tube - Videos Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db import DatabaseManager


class VideosTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()
        # Map treeview item IDs to database video IDs
        self._item_to_video_id = {}

        self.create_videos_view()

    def create_videos_view(self):
        """Create videos table layout"""
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_header(main_frame)
        self.create_table(main_frame)
        self.create_detail_panel(main_frame)
        self.create_action_buttons(main_frame)

    def create_header(self, parent):
        """Create header with filters and search"""
        header_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        header_frame.pack(fill="x", pady=(0, 20))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Video Tracking",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title_label.pack(side="left", padx=20, pady=15)

        # Search entry
        search_label = ctk.CTkLabel(
            header_frame,
            text="Search:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"]
        )
        search_label.pack(side="left", padx=(30, 5), pady=15)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_current_view())
        self.search_entry = ctk.CTkEntry(
            header_frame,
            textvariable=self.search_var,
            placeholder_text="Filter by title...",
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            width=180,
            height=35
        )
        self.search_entry.pack(side="left", pady=15)

        # Filter dropdown
        filter_label = ctk.CTkLabel(
            header_frame,
            text="Status:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"]
        )
        filter_label.pack(side="left", padx=(20, 5), pady=15)

        self.filter_dropdown = ctk.CTkOptionMenu(
            header_frame,
            values=["All", "Pending", "Uploaded", "Monitoring", "Success", "Retry", "Abandoned"],
            fg_color=self.theme["button_bg"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            width=140,
            command=self.filter_videos
        )
        self.filter_dropdown.set("All")
        self.filter_dropdown.pack(side="left", pady=15)

        # Sort dropdown
        sort_label = ctk.CTkLabel(
            header_frame,
            text="Sort:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"]
        )
        sort_label.pack(side="left", padx=(20, 5), pady=15)

        self.sort_dropdown = ctk.CTkOptionMenu(
            header_frame,
            values=["Newest First", "Oldest First", "Most Views", "Highest CTR", "Highest Engagement"],
            fg_color=self.theme["button_bg"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            width=160,
            command=lambda _: self._apply_current_view()
        )
        self.sort_dropdown.set("Newest First")
        self.sort_dropdown.pack(side="left", pady=15)

        # Refresh button
        refresh_button = ctk.CTkButton(
            header_frame,
            text="↻ Refresh",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=100,
            height=35,
            corner_radius=8,
            command=self.refresh_table
        )
        refresh_button.pack(side="right", padx=20, pady=15)

        # Video count label
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="0 videos",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"]
        )
        self.count_label.pack(side="right", padx=(0, 10), pady=15)

    def create_table(self, parent):
        """Create videos table"""
        table_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Create treeview with custom styling
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Videos.Treeview",
            background=self.theme["bg_tertiary"],
            foreground=self.theme["text_primary"],
            fieldbackground=self.theme["bg_tertiary"],
            borderwidth=0,
            font=(self.theme["font_family"], self.theme["font_size_body"])
        )

        style.configure(
            "Videos.Treeview.Heading",
            background=self.theme["bg_secondary"],
            foreground=self.theme["text_primary"],
            borderwidth=0,
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold")
        )

        style.map(
            "Videos.Treeview",
            background=[("selected", self.theme["accent"])],
            foreground=[("selected", "#FFFFFF")]
        )

        # Create scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Create treeview
        columns = ("Title", "Status", "Attempt", "Views", "CTR", "Engagement", "Likes", "Uploaded")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Videos.Treeview",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )

        scrollbar.configure(command=self.tree.yview)

        # Configure columns
        col_config = {
            "Title": 280,
            "Status": 100,
            "Attempt": 70,
            "Views": 80,
            "CTR": 70,
            "Engagement": 100,
            "Likes": 70,
            "Uploaded": 140,
        }
        for col, width in col_config.items():
            self.tree.heading(col, text=col if col != "CTR" else "CTR %",
                            command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=width)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Bind selection event for detail panel
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Load data
        self.load_videos()

    def create_detail_panel(self, parent):
        """Create a collapsible detail panel for the selected video"""
        self.detail_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10,
            height=0
        )
        self.detail_frame.pack(fill="x", pady=(0, 10))
        self.detail_frame.pack_propagate(False)

        # Detail labels (created but hidden until selection)
        self._detail_labels = {}
        detail_grid = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        detail_grid.pack(fill="x", padx=20, pady=10)

        fields = ["Title", "YouTube ID", "Keywords", "Tags", "Description"]
        for i, field in enumerate(fields):
            lbl = ctk.CTkLabel(
                detail_grid,
                text=f"{field}:",
                font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                text_color=self.theme["text_secondary"],
                anchor="w"
            )
            lbl.grid(row=i, column=0, sticky="nw", padx=(0, 10), pady=2)

            val = ctk.CTkLabel(
                detail_grid,
                text="—",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_primary"],
                anchor="w",
                wraplength=600
            )
            val.grid(row=i, column=1, sticky="w", pady=2)
            self._detail_labels[field] = val

    def create_action_buttons(self, parent):
        """Create action buttons for selected video"""
        action_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        action_frame.pack(fill="x")

        # Manual retry button
        retry_button = ctk.CTkButton(
            action_frame,
            text="Retry Selected",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["warning"],
            hover_color=self.theme["warning"],
            text_color="#FFFFFF",
            height=45,
            corner_radius=8,
            command=self.retry_selected
        )
        retry_button.pack(side="left", padx=(0, 10))

        # Delete button
        delete_button = ctk.CTkButton(
            action_frame,
            text="Delete Selected",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["error"],
            hover_color=self.theme["error"],
            text_color="#FFFFFF",
            height=45,
            corner_radius=8,
            command=self.delete_selected
        )
        delete_button.pack(side="left", padx=(0, 10))

        # Export button
        export_button = ctk.CTkButton(
            action_frame,
            text="Export CSV",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text_primary"],
            height=45,
            corner_radius=8,
            command=self.export_csv
        )
        export_button.pack(side="right")

    # ── Data loading ──────────────────────────────────────────────

    def _safe_str(self, value, default=""):
        """Return value as string, substituting default for None."""
        return str(value) if value is not None else default

    def _safe_float(self, value, default=0.0):
        """Return value as float, substituting default for None."""
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value, default=0):
        """Return value as int, substituting default for None."""
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    def load_videos(self, status_filter=None, search_text=None):
        """Load videos from database into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_to_video_id.clear()

        try:
            if status_filter and status_filter != "All":
                videos = self.db.get_videos_by_status(status_filter.lower())
            else:
                videos = self.db.get_all_videos()

            # Apply search filter
            if search_text:
                search_lower = search_text.lower()
                videos = [
                    v for v in videos
                    if search_lower in (self._safe_str(v.get('title_used'), '')).lower()
                ]

            # Apply sort
            videos = self._sort_videos(videos)

            if videos:
                for video in videos:
                    title_raw = self._safe_str(video.get('title_used'), 'Untitled')
                    title = (title_raw[:45] + "...") if len(title_raw) > 45 else title_raw
                    status = self._safe_str(video.get('status'), 'unknown').title()
                    attempt = f"{self._safe_int(video.get('attempt_number'), 1)}/{self._safe_int(video.get('max_attempts'), 3)}"
                    views = str(self._safe_int(video.get('views')))
                    ctr = f"{self._safe_float(video.get('ctr')):.1f}"
                    engagement = f"{self._safe_float(video.get('engagement_rate')):.1f}"
                    likes = str(self._safe_int(video.get('likes')))

                    upload_date_raw = video.get('upload_date') or video.get('created_at') or ''
                    upload_date = self._safe_str(upload_date_raw)[:16] if upload_date_raw else 'Pending'

                    item_id = self.tree.insert("", "end", values=(
                        title, status, attempt, views, ctr, engagement, likes, upload_date
                    ))
                    self._item_to_video_id[item_id] = video['id']
            else:
                self.tree.insert("", "end", values=(
                    "No videos found", "—", "—", "—", "—", "—", "—", "—"
                ))

            # Update count
            count = len(videos) if videos else 0
            self.count_label.configure(text=f"{count} video{'s' if count != 1 else ''}")

        except Exception as e:
            print(f"Error loading videos: {e}")
            self.tree.insert("", "end", values=(
                "Error loading data", "—", "—", "—", "—", "—", "—", "—"
            ))
            self.count_label.configure(text="Error")

    def _sort_videos(self, videos):
        """Sort videos list based on current sort dropdown selection."""
        sort_key = self.sort_dropdown.get()
        sort_map = {
            "Newest First": lambda v: v.get('created_at') or '',
            "Oldest First": lambda v: v.get('created_at') or '',
            "Most Views": lambda v: self._safe_int(v.get('views')),
            "Highest CTR": lambda v: self._safe_float(v.get('ctr')),
            "Highest Engagement": lambda v: self._safe_float(v.get('engagement_rate')),
        }
        key_fn = sort_map.get(sort_key, sort_map["Newest First"])
        reverse = sort_key != "Oldest First"
        try:
            return sorted(videos, key=key_fn, reverse=reverse)
        except Exception:
            return videos

    def _get_selected_video_id(self):
        """Get the database ID of the currently selected video, or None."""
        selection = self.tree.selection()
        if not selection:
            return None
        return self._item_to_video_id.get(selection[0])

    # ── Event handlers ────────────────────────────────────────────

    def _on_select(self, event=None):
        """Show detail panel for the selected video."""
        video_id = self._get_selected_video_id()
        if video_id is None:
            self.detail_frame.configure(height=0)
            return

        video = self.db.get_video(video_id)
        if not video:
            self.detail_frame.configure(height=0)
            return

        import json
        self._detail_labels["Title"].configure(
            text=self._safe_str(video.get('title_used'), 'Untitled'))
        self._detail_labels["YouTube ID"].configure(
            text=self._safe_str(video.get('youtube_video_id'), 'N/A'))

        kw_raw = video.get('keywords_targeted') or '[]'
        try:
            keywords = json.loads(kw_raw) if isinstance(kw_raw, str) else kw_raw
            self._detail_labels["Keywords"].configure(text=", ".join(keywords) if keywords else "None")
        except (json.JSONDecodeError, TypeError):
            self._detail_labels["Keywords"].configure(text=self._safe_str(kw_raw))

        tags_raw = video.get('tags_used') or '[]'
        try:
            tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
            self._detail_labels["Tags"].configure(text=", ".join(tags) if tags else "None")
        except (json.JSONDecodeError, TypeError):
            self._detail_labels["Tags"].configure(text=self._safe_str(tags_raw))

        desc = self._safe_str(video.get('description_used'), 'No description')
        self._detail_labels["Description"].configure(
            text=(desc[:200] + "...") if len(desc) > 200 else desc)

        self.detail_frame.configure(height=140)

    def _apply_current_view(self, *_args):
        """Re-apply current filter, search, and sort."""
        self.load_videos(
            status_filter=self.filter_dropdown.get(),
            search_text=self.search_var.get() or None
        )

    def filter_videos(self, filter_value):
        """Filter videos by status"""
        self.load_videos(
            status_filter=filter_value,
            search_text=self.search_var.get() or None
        )
        self.app.dashboard_tab.add_log_entry(f"Filtered videos: {filter_value}", "INFO")

    def refresh_table(self):
        """Refresh video table from database"""
        self._apply_current_view()
        self.app.dashboard_tab.add_log_entry("Video table refreshed", "INFO")

    def retry_selected(self):
        """Retry selected video — marks it for retry in the database"""
        video_id = self._get_selected_video_id()
        if video_id is None:
            self.app.dashboard_tab.add_log_entry("No video selected for retry", "ERROR")
            return

        video = self.db.get_video(video_id)
        if not video:
            self.app.dashboard_tab.add_log_entry("Video not found in database", "ERROR")
            return

        max_attempts = self._safe_int(video.get('max_attempts'), 3)
        current_attempt = self._safe_int(video.get('attempt_number'), 1)

        if current_attempt >= max_attempts:
            self.app.dashboard_tab.add_log_entry(
                f"Video already at max attempts ({max_attempts})", "WARNING")
            return

        if video.get('status') == 'success':
            self.app.dashboard_tab.add_log_entry(
                "Cannot retry a successful video", "WARNING")
            return

        title = self._safe_str(video.get('title_used'), 'Untitled')
        self.db.mark_for_retry(video_id, reason="Manual retry from Videos tab")
        self._apply_current_view()
        self.app.dashboard_tab.add_log_entry(
            f"Manual retry initiated: {title} (attempt {current_attempt + 1}/{max_attempts})",
            "WARNING"
        )

    def delete_selected(self):
        """Delete selected video from database after confirmation"""
        video_id = self._get_selected_video_id()
        if video_id is None:
            self.app.dashboard_tab.add_log_entry("No video selected for deletion", "ERROR")
            return

        video = self.db.get_video(video_id)
        if not video:
            self.app.dashboard_tab.add_log_entry("Video not found in database", "ERROR")
            return

        title = self._safe_str(video.get('title_used'), 'Untitled')

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete:\n\n{title}\n\nThis cannot be undone."
        )
        if not confirm:
            return

        self.db.delete_video(video_id)
        self._apply_current_view()
        self.detail_frame.configure(height=0)
        self.app.dashboard_tab.add_log_entry(f"Video deleted: {title}", "WARNING")

    def export_csv(self):
        """Export current video list to CSV"""
        from tkinter import filedialog
        import csv

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Videos"
        )
        if not filepath:
            return

        try:
            videos = self.db.get_all_videos()
            if not videos:
                self.app.dashboard_tab.add_log_entry("No videos to export", "WARNING")
                return

            fieldnames = [
                "id", "title_used", "status", "attempt_number", "views",
                "ctr", "engagement_rate", "likes", "comments", "impressions",
                "watch_time_minutes", "youtube_video_id", "upload_date",
                "keywords_targeted", "tags_used"
            ]

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for v in videos:
                    writer.writerow(v)

            self.app.dashboard_tab.add_log_entry(
                f"Exported {len(videos)} videos to {filepath}", "SUCCESS")
        except Exception as e:
            self.app.dashboard_tab.add_log_entry(f"Export failed: {e}", "ERROR")
