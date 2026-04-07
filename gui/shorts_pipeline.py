"""
RealE Tube - Shorts Pipeline Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager


class ShortsPipelineTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        # Map treeview item IDs to database upload IDs
        self._item_to_upload_id = {}

        self.create_shorts_pipeline()

    # ── Helpers ────────────────────────────────────────────────────

    def _safe_int(self, value, default=0):
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    def _safe_float(self, value, default=0.0):
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    # ── Layout ─────────────────────────────────────────────────────

    def create_shorts_pipeline(self):
        """Create the main Shorts Pipeline layout."""
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        # Scrollable content area
        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_info_section(scroll)
        self._create_upload_form(scroll)
        self._create_queue_table(scroll)
        self._create_performance_summary(scroll)
        self._create_action_buttons(scroll)

    # ── Header ─────────────────────────────────────────────────────

    def _create_header(self, parent):
        """Create header bar with title, under-construction badge, and refresh."""
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="Shorts Pipeline",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(side="left")

        badge = under_construction_badge(bar, self.theme)
        badge.pack(side="left", padx=(8, 0))

        refresh_btn = ctk.CTkButton(
            bar,
            text="↻ Refresh",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=100,
            height=32,
            corner_radius=8,
            command=self.refresh_pipeline,
        )
        refresh_btn.pack(side="right")

    # ── Info Section ───────────────────────────────────────────────

    def _create_info_section(self, parent):
        """Explain Shorts strategy to the user."""
        info_frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        info_frame.pack(fill="x", pady=(0, 20))

        info_title = ctk.CTkLabel(
            info_frame,
            text="YouTube Shorts Strategy",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        info_title.pack(fill="x", padx=20, pady=(15, 5))

        info_text = (
            "Shorts are vertical videos under 60 seconds that appear in the dedicated "
            "Shorts shelf on YouTube. They use a different keyword and discovery approach "
            "compared to long-form content — hashtags and trending sounds matter more than "
            "traditional SEO. Use this pipeline to queue, schedule, and track your Shorts "
            "separately from regular uploads."
        )
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
            anchor="w",
            justify="left",
            wraplength=700,
        )
        info_label.pack(fill="x", padx=20, pady=(0, 15))

    # ── Upload Form ────────────────────────────────────────────────

    def _create_upload_form(self, parent):
        """Create the form for queuing a new Short."""
        form_frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        form_frame.pack(fill="x", pady=(0, 20))

        form_title = ctk.CTkLabel(
            form_frame,
            text="Queue a New Short",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        form_title.pack(fill="x", padx=20, pady=(15, 10))

        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=(0, 15))
        fields_frame.grid_columnconfigure(1, weight=1)

        # File path
        ctk.CTkLabel(
            fields_frame,
            text="File Path:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)

        self.file_path_var = ctk.StringVar()
        ctk.CTkEntry(
            fields_frame,
            textvariable=self.file_path_var,
            placeholder_text="/path/to/short_video.mp4",
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            height=35,
        ).grid(row=0, column=1, sticky="ew", pady=5)

        # Description
        ctk.CTkLabel(
            fields_frame,
            text="Description:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)

        self.description_var = ctk.StringVar()
        ctk.CTkEntry(
            fields_frame,
            textvariable=self.description_var,
            placeholder_text="Short description or hashtags",
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            height=35,
        ).grid(row=1, column=1, sticky="ew", pady=5)

        # Schedule datetime
        ctk.CTkLabel(
            fields_frame,
            text="Schedule:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)

        self.schedule_var = ctk.StringVar()
        ctk.CTkEntry(
            fields_frame,
            textvariable=self.schedule_var,
            placeholder_text="YYYY-MM-DD HH:MM",
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            width=200,
            height=35,
        ).grid(row=2, column=1, sticky="w", pady=5)

        # Is Short toggle
        self.is_short_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            fields_frame,
            text="Mark as Short",
            variable=self.is_short_var,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            progress_color=self.theme["accent"],
        ).grid(row=3, column=1, sticky="w", pady=5)

        # Queue button
        ctk.CTkButton(
            form_frame,
            text="Queue Short",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=140,
            height=36,
            corner_radius=8,
            command=self._queue_short,
        ).pack(padx=20, pady=(0, 15), anchor="e")

    # ── Queue Table ────────────────────────────────────────────────

    def _create_queue_table(self, parent):
        """Create Treeview table showing queued Shorts."""
        table_frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        table_frame.pack(fill="x", pady=(0, 20))

        table_title = ctk.CTkLabel(
            table_frame,
            text="Shorts Queue",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        table_title.pack(fill="x", padx=20, pady=(15, 10))

        columns = ("file", "description", "scheduled", "status")
        self.queue_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=8
        )
        self.queue_tree.heading("file", text="File")
        self.queue_tree.heading("description", text="Description")
        self.queue_tree.heading("scheduled", text="Scheduled")
        self.queue_tree.heading("status", text="Status")

        self.queue_tree.column("file", width=220, minwidth=120)
        self.queue_tree.column("description", width=260, minwidth=120)
        self.queue_tree.column("scheduled", width=150, minwidth=100)
        self.queue_tree.column("status", width=100, minwidth=80)

        self.queue_tree.pack(fill="x", padx=20, pady=(0, 15))

        self._populate_queue()

    # ── Performance Summary ────────────────────────────────────────

    def _create_performance_summary(self, parent):
        """Show Shorts-specific performance metrics."""
        perf_frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        perf_frame.pack(fill="x", pady=(0, 20))

        perf_title = ctk.CTkLabel(
            perf_frame,
            text="Shorts Performance",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        perf_title.pack(fill="x", padx=20, pady=(15, 10))

        metrics_row = ctk.CTkFrame(perf_frame, fg_color="transparent")
        metrics_row.pack(fill="x", padx=20, pady=(0, 15))
        metrics_row.grid_columnconfigure((0, 1), weight=1)

        shorts_count, avg_views = self._compute_shorts_metrics()

        # Shorts uploaded count
        self.shorts_count_label = ctk.CTkLabel(
            metrics_row,
            text=str(shorts_count),
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["accent"],
        )
        self.shorts_count_label.grid(row=0, column=0, pady=(0, 2))
        ctk.CTkLabel(
            metrics_row,
            text="Shorts Uploaded",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        ).grid(row=1, column=0)

        # Average views
        self.avg_views_label = ctk.CTkLabel(
            metrics_row,
            text=f"{avg_views:,.0f}",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["success"],
        )
        self.avg_views_label.grid(row=0, column=1, pady=(0, 2))
        ctk.CTkLabel(
            metrics_row,
            text="Avg Views (Shorts)",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        ).grid(row=1, column=1)

    # ── Action Buttons ─────────────────────────────────────────────

    def _create_action_buttons(self, parent):
        """Upload Now and Remove from Queue buttons."""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Upload Now",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["success"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=140,
            height=36,
            corner_radius=8,
            command=self._upload_now,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Remove from Queue",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["error"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            width=160,
            height=36,
            corner_radius=8,
            command=self._remove_from_queue,
        ).pack(side="left")

    # ── Data helpers ───────────────────────────────────────────────

    def _populate_queue(self):
        """Load scheduled uploads filtered to Shorts only."""
        self.queue_tree.delete(*self.queue_tree.get_children())
        self._item_to_upload_id.clear()

        uploads = self.db.get_scheduled_uploads()
        for upload in uploads:
            if self._safe_int(upload.get("is_short")) != 1:
                continue
            item_id = self.queue_tree.insert(
                "",
                "end",
                values=(
                    upload.get("file_path", ""),
                    upload.get("description", ""),
                    upload.get("scheduled_at", ""),
                    upload.get("status", "pending"),
                ),
            )
            self._item_to_upload_id[item_id] = upload["id"]

    def _compute_shorts_metrics(self):
        """Return (count_of_shorts_uploaded, average_views)."""
        uploads = self.db.get_scheduled_uploads()
        shorts = [u for u in uploads if self._safe_int(u.get("is_short")) == 1]
        count = len(shorts)
        if count == 0:
            return 0, 0.0
        total_views = sum(self._safe_float(s.get("views", 0)) for s in shorts)
        return count, total_views / count

    # ── Actions ────────────────────────────────────────────────────

    def _queue_short(self):
        """Validate form fields and add scheduled upload with is_short=1."""
        file_path = self.file_path_var.get().strip()
        description = self.description_var.get().strip()
        scheduled_at = self.schedule_var.get().strip()

        if not file_path:
            messagebox.showwarning("Missing Field", "Please enter a file path.")
            return
        if not scheduled_at:
            messagebox.showwarning("Missing Field", "Please enter a schedule datetime.")
            return

        is_short = 1 if self.is_short_var.get() else 0
        self.db.add_scheduled_upload(
            file_path=file_path,
            description=description,
            scheduled_at=scheduled_at,
            is_short=is_short,
        )

        # Reset form
        self.file_path_var.set("")
        self.description_var.set("")
        self.schedule_var.set("")
        self.is_short_var.set(True)

        self.refresh_pipeline()
        messagebox.showinfo("Queued", "Short has been added to the upload queue.")

    def _upload_now(self):
        """Mark the selected queue entry for immediate upload."""
        selected = self.queue_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a Short from the queue.")
            return

        upload_id = self._item_to_upload_id.get(selected[0])
        if upload_id is None:
            return

        self.db.update_scheduled_status(upload_id, "uploading")
        self.refresh_pipeline()
        messagebox.showinfo("Upload Started", "Short has been marked for immediate upload.")

    def _remove_from_queue(self):
        """Delete the selected entry from the queue."""
        selected = self.queue_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a Short to remove.")
            return

        upload_id = self._item_to_upload_id.get(selected[0])
        if upload_id is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Removal", "Remove this Short from the queue?"
        )
        if not confirm:
            return

        self.db.delete_scheduled_upload(upload_id)
        self.refresh_pipeline()

    # ── Refresh ────────────────────────────────────────────────────

    def refresh_pipeline(self):
        """Reload queue table and performance metrics."""
        self._populate_queue()
        shorts_count, avg_views = self._compute_shorts_metrics()
        self.shorts_count_label.configure(text=str(shorts_count))
        self.avg_views_label.configure(text=f"{avg_views:,.0f}")
