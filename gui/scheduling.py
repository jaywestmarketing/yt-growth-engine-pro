"""
RealE Tube - Scheduling & Queue Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk, filedialog

from gui.tooltip import under_construction_badge
from database.db import DatabaseManager


class SchedulingTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        # Dynamic widget references
        self._tree = None
        self._summary_labels = {}
        self._file_path_var = ctk.StringVar()
        self._desc_var = ctk.StringVar()
        self._date_var = ctk.StringVar()
        self._channel_var = ctk.StringVar()
        self._channel_map = {}

        self.create_scheduling()

    # ── Helpers ────────────────────────────────────────────────────

    def _safe_int(self, value, default=0):
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    # ── Layout ────────────────────────────────────────────────────

    def create_scheduling(self):
        """Build the full scheduling tab layout."""
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_schedule_form(scroll)
        self._create_queue_table(scroll)
        self._create_summary_cards(scroll)
        self._create_action_buttons(scroll)

        self.refresh_data()

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="Upload Schedule & Queue",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(side="left")

        badge = under_construction_badge(bar, self.theme, "This feature is under construction")
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
            command=self.refresh_data,
        )
        btn.pack(side="right")

    # ── Schedule Form ─────────────────────────────────────────────

    def _create_schedule_form(self, parent):
        form_frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            form_frame,
            text="Schedule New Upload",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 12))

        fields = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields.pack(fill="x", padx=20, pady=(0, 16))
        fields.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Row 0 – File path
        ctk.CTkLabel(
            fields,
            text="Video File",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=0, column=0, sticky="w", padx=4, pady=(0, 2))

        path_frame = ctk.CTkFrame(fields, fg_color="transparent")
        path_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 8))
        path_frame.grid_columnconfigure(0, weight=1)

        path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self._file_path_var,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            height=34,
        )
        path_entry.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            path_frame,
            text="Browse",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            width=70,
            height=34,
            corner_radius=6,
            command=self._browse_file,
        ).grid(row=0, column=1, padx=(6, 0))

        # Row 0 – Description
        ctk.CTkLabel(
            fields,
            text="Description",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=0, column=2, sticky="w", padx=4, pady=(0, 2))

        ctk.CTkEntry(
            fields,
            textvariable=self._desc_var,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            height=34,
        ).grid(row=1, column=2, columnspan=2, sticky="ew", padx=4, pady=(0, 8))

        # Row 2 – Date picker
        ctk.CTkLabel(
            fields,
            text="Scheduled Date/Time",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=2, column=0, sticky="w", padx=4, pady=(0, 2))

        date_entry = ctk.CTkEntry(
            fields,
            textvariable=self._date_var,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_tertiary"],
            placeholder_text="YYYY-MM-DD HH:MM",
            height=34,
        )
        date_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 8))

        # Row 2 – Channel selector
        ctk.CTkLabel(
            fields,
            text="Channel",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=2, column=2, sticky="w", padx=4, pady=(0, 2))

        channels = self.db.get_all_channels()
        channel_names = []
        for ch in channels:
            name = ch.get("channel_name", "Unknown")
            channel_names.append(name)
            self._channel_map[name] = ch.get("id")

        self._channel_dropdown = ctk.CTkComboBox(
            fields,
            values=channel_names if channel_names else ["No channels"],
            variable=self._channel_var,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            height=34,
            state="readonly" if channel_names else "disabled",
        )
        self._channel_dropdown.grid(row=3, column=2, columnspan=2, sticky="ew", padx=4, pady=(0, 8))

        # Submit button
        ctk.CTkButton(
            form_frame,
            text="Schedule Upload",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            height=38,
            corner_radius=8,
            command=self._schedule_upload,
        ).pack(padx=20, pady=(0, 16), anchor="e")

    # ── Queue Table ───────────────────────────────────────────────

    def _create_queue_table(self, parent):
        table_frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 16))

        ctk.CTkLabel(
            table_frame,
            text="Upload Queue",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 8))

        columns = ("file", "description", "scheduled", "channel", "status")
        self._tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self._tree.heading("file", text="File")
        self._tree.heading("description", text="Description")
        self._tree.heading("scheduled", text="Scheduled Time")
        self._tree.heading("channel", text="Channel")
        self._tree.heading("status", text="Status")

        self._tree.column("file", width=180, minwidth=120)
        self._tree.column("description", width=200, minwidth=100)
        self._tree.column("scheduled", width=140, minwidth=100)
        self._tree.column("channel", width=120, minwidth=80)
        self._tree.column("status", width=90, minwidth=60)

        self._tree.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    # ── Summary Cards ─────────────────────────────────────────────

    def _create_summary_cards(self, parent):
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 16))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        definitions = [
            ("queued", "Queued", self.theme["accent"]),
            ("completed", "Completed", self.theme["success"]),
            ("failed", "Failed", self.theme["error"]),
        ]

        for idx, (key, label, color) in enumerate(definitions):
            card = ctk.CTkFrame(cards_frame, fg_color=self.theme["bg_secondary"], corner_radius=10)
            card.grid(row=0, column=idx, sticky="ew", padx=6)

            ctk.CTkLabel(
                card,
                text=label,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"],
            ).pack(padx=16, pady=(12, 2))

            val_label = ctk.CTkLabel(
                card,
                text="0",
                font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
                text_color=color,
            )
            val_label.pack(padx=16, pady=(0, 12))
            self._summary_labels[key] = val_label

    # ── Action Buttons ────────────────────────────────────────────

    def _create_action_buttons(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="Cancel Selected",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["warning"],
            hover_color=self.theme["error"],
            text_color="#FFFFFF",
            width=140,
            height=34,
            corner_radius=8,
            command=self._cancel_selected,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="Upload Now",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=120,
            height=34,
            corner_radius=8,
            command=self._upload_now,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="Clear Completed",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            text_color="#FFFFFF",
            width=140,
            height=34,
            corner_radius=8,
            command=self._clear_completed,
        ).pack(side="left")

    # ── Commands ──────────────────────────────────────────────────

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")],
        )
        if path:
            self._file_path_var.set(path)

    def _schedule_upload(self):
        file_path = self._file_path_var.get().strip()
        description = self._desc_var.get().strip()
        scheduled_at = self._date_var.get().strip()
        channel_name = self._channel_var.get().strip()
        channel_id = self._channel_map.get(channel_name)

        if not file_path or not scheduled_at:
            return

        self.db.add_scheduled_upload(
            file_path=file_path,
            description=description,
            scheduled_at=scheduled_at,
            channel_id=channel_id,
        )

        self._file_path_var.set("")
        self._desc_var.set("")
        self._date_var.set("")
        self.refresh_data()

    def _cancel_selected(self):
        selected = self._tree.selection()
        for item in selected:
            upload_id = self._tree.item(item, "values")[-1]  # hidden id stored in status col tag
            rid = self._tree.item(item, "tags")
            if rid:
                self.db.update_scheduled_status(int(rid[0]), "cancelled")
        self.refresh_data()

    def _upload_now(self):
        selected = self._tree.selection()
        for item in selected:
            rid = self._tree.item(item, "tags")
            if rid:
                self.db.update_scheduled_status(int(rid[0]), "uploading")
        self.refresh_data()

    def _clear_completed(self):
        uploads = self.db.get_scheduled_uploads(status="completed")
        for u in uploads:
            self.db.delete_scheduled_upload(u["id"])
        self.refresh_data()

    # ── Refresh ───────────────────────────────────────────────────

    def refresh_data(self):
        """Reload queue table and summary counts from the database."""
        uploads = self.db.get_scheduled_uploads()

        # Refresh table
        if self._tree:
            for row in self._tree.get_children():
                self._tree.delete(row)
            for u in uploads:
                fname = u.get("file_path", "").rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
                self._tree.insert(
                    "",
                    "end",
                    values=(
                        fname,
                        u.get("description", ""),
                        u.get("scheduled_at", ""),
                        u.get("channel_id", "—"),
                        u.get("status", "queued"),
                    ),
                    tags=(str(u.get("id", "")),),
                )

        # Refresh summary cards
        counts = {"queued": 0, "completed": 0, "failed": 0}
        for u in uploads:
            status = u.get("status", "queued")
            if status in counts:
                counts[status] += 1

        for key, label in self._summary_labels.items():
            label.configure(text=str(counts.get(key, 0)))
