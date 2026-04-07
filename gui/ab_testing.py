"""
RealE Tube - A/B Thumbnail Testing Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk

from database.db import DatabaseManager
from gui.tooltip import under_construction_badge


class ABTestingTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()

        # Cached video list for the dropdown
        self._video_map = {}  # display_text -> video_id
        self._variant_entries = []

        self.create_tab()

    # ── Helpers ────────────────────────────────────────────────────

    def _safe_float(self, value, default=0.0):
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    # ── Main layout ───────────────────────────────────────────────

    def create_tab(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)

        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._create_new_test_form(scroll)
        self._create_tests_table(scroll)
        self._create_action_buttons(scroll)

        self.refresh_data()

    # ── Header ────────────────────────────────────────────────────

    def _create_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="A/B Thumbnail Testing",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(side="left")

        badge = under_construction_badge(bar, self.theme)
        badge.pack(side="left", padx=(8, 0))

        btn = ctk.CTkButton(
            bar,
            text="\u21bb Refresh",
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

    # ── New-test form ─────────────────────────────────────────────

    def _create_new_test_form(self, parent):
        form_frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        form_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            form_frame,
            text="Create New Test",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Video selector row
        video_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        video_row.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            video_row,
            text="Video:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            width=80,
            anchor="w",
        ).pack(side="left")

        self._video_dropdown_var = ctk.StringVar(value="")
        self._video_dropdown = ctk.CTkComboBox(
            video_row,
            variable=self._video_dropdown_var,
            values=["Loading..."],
            width=400,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            state="readonly",
        )
        self._video_dropdown.pack(side="left", padx=(8, 0))

        # Variant entries (A, B, C)
        self._variant_entries = []
        for label in ("A", "B", "C"):
            row = ctk.CTkFrame(form_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=(0, 6))

            ctk.CTkLabel(
                row,
                text=f"Variant {label}:",
                font=(self.theme["font_family"], self.theme["font_size_body"]),
                text_color=self.theme["text_secondary"],
                width=80,
                anchor="w",
            ).pack(side="left")

            path_var = ctk.StringVar()
            entry = ctk.CTkEntry(
                row,
                textvariable=path_var,
                placeholder_text=f"Thumbnail file path for variant {label}",
                width=340,
                font=(self.theme["font_family"], self.theme["font_size_body"]),
            )
            entry.pack(side="left", padx=(8, 4))

            browse_btn = ctk.CTkButton(
                row,
                text="Browse",
                width=70,
                height=28,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                fg_color=self.theme["button_bg"],
                hover_color=self.theme["button_hover"],
                command=lambda v=path_var: self._browse_thumbnail(v),
            )
            browse_btn.pack(side="left")

            self._variant_entries.append((label, path_var))

        # Create button
        ctk.CTkButton(
            form_frame,
            text="Create Test",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=140,
            height=36,
            corner_radius=8,
            command=self._create_test,
        ).pack(anchor="e", padx=16, pady=(4, 16))

    def _browse_thumbnail(self, path_var):
        path = filedialog.askopenfilename(
            title="Select Thumbnail Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")],
        )
        if path:
            path_var.set(path)

    # ── Tests table ───────────────────────────────────────────────

    def _create_tests_table(self, parent):
        table_frame = ctk.CTkFrame(
            parent, fg_color=self.theme["bg_secondary"], corner_radius=10
        )
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        ctk.CTkLabel(
            table_frame,
            text="Existing Tests",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        columns = ("Video", "Variant", "Impressions", "Clicks", "CTR%", "Status")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=10
        )
        for col in columns:
            self._tree.heading(col, text=col)
        self._tree.column("Video", width=220)
        self._tree.column("Variant", width=80, anchor="center")
        self._tree.column("Impressions", width=100, anchor="center")
        self._tree.column("Clicks", width=80, anchor="center")
        self._tree.column("CTR%", width=80, anchor="center")
        self._tree.column("Status", width=100, anchor="center")

        self._tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    # ── Action buttons ────────────────────────────────────────────

    def _create_action_buttons(self, parent):
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            btn_row,
            text="Set Winner",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["success"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=120,
            height=34,
            corner_radius=8,
            command=self._set_winner,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Delete Test",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["error"],
            hover_color=self.theme["warning"],
            text_color="#FFFFFF",
            width=120,
            height=34,
            corner_radius=8,
            command=self._delete_test,
        ).pack(side="left")

    # ── Data operations ───────────────────────────────────────────

    def refresh_data(self):
        self._load_videos()
        self._load_tests()

    def _load_videos(self):
        try:
            videos = self.db.get_all_videos()
        except Exception:
            videos = []
        self._video_map.clear()
        display_list = []
        for v in videos:
            title = v.get("title_used") or v.get("file_path") or f"Video #{v['id']}"
            display = f"{v['id']} - {title}"
            display_list.append(display)
            self._video_map[display] = v["id"]
        self._video_dropdown.configure(values=display_list if display_list else ["No videos found"])
        if display_list:
            self._video_dropdown_var.set(display_list[0])
        else:
            self._video_dropdown_var.set("")

    def _load_tests(self):
        for row in self._tree.get_children():
            self._tree.delete(row)
        try:
            tests = self.db.get_all_thumbnail_tests()
        except Exception:
            tests = []
        for t in tests:
            video_title = t.get("title_used") or f"Video #{t.get('video_id', '?')}"
            ctr = self._safe_float(t.get("ctr"))
            is_winner = t.get("is_winner", 0)
            is_active = t.get("is_active", 0)
            status = "Winner" if is_winner else ("Active" if is_active else "Inactive")
            self._tree.insert(
                "",
                tk.END,
                iid=str(t["id"]),
                values=(
                    video_title,
                    t.get("variant_label", ""),
                    t.get("impressions", 0),
                    t.get("clicks", 0),
                    f"{ctr:.2f}",
                    status,
                ),
            )

    def _create_test(self):
        selected = self._video_dropdown_var.get()
        video_id = self._video_map.get(selected)
        if not video_id:
            messagebox.showwarning("No Video", "Please select a video first.")
            return

        created = 0
        for label, path_var in self._variant_entries:
            path = path_var.get().strip()
            if not path:
                continue
            try:
                self.db.add_thumbnail_test(video_id, label, path)
                created += 1
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to create variant {label}: {exc}")
        if created == 0:
            messagebox.showwarning("Empty", "Enter at least one thumbnail path.")
            return

        # Clear fields and refresh
        for _, path_var in self._variant_entries:
            path_var.set("")
        self.refresh_data()

    def _set_winner(self):
        selected = self._tree.selection()
        if not selected:
            messagebox.showinfo("Select Row", "Select a test row to mark as winner.")
            return
        test_id = int(selected[0])
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE thumbnail_tests SET is_winner = 1, is_active = 0 WHERE id = ?", (test_id,))
            conn.commit()
            conn.close()
        except Exception as exc:
            messagebox.showerror("Error", f"Could not set winner: {exc}")
            return
        self.refresh_data()

    def _delete_test(self):
        selected = self._tree.selection()
        if not selected:
            messagebox.showinfo("Select Row", "Select a test row to delete.")
            return
        test_id = int(selected[0])
        if not messagebox.askyesno("Confirm", f"Delete test #{test_id}?"):
            return
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM thumbnail_tests WHERE id = ?", (test_id,))
            conn.commit()
            conn.close()
        except Exception as exc:
            messagebox.showerror("Error", f"Could not delete test: {exc}")
            return
        self.refresh_data()
