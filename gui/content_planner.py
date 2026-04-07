"""
RealE Tube - AI Content Planner Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager


class ContentPlannerTab:
    """AI-assisted content planning tab with manual and generated plans."""

    CONTENT_TYPES = ["Tutorial", "Review", "Comparison", "How-To", "Listicle", "Reaction"]

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()
        self._selected_plan_id = None

        self._build_layout()
        self._load_plans()

    # ── Layout ────────────────────────────────────────────────────

    def _build_layout(self):
        """Assemble every section of the content-planner tab."""
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_header(main)

        scroll = ctk.CTkScrollableFrame(main, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._build_generate_form(scroll)
        self._build_manual_form(scroll)
        self._build_plans_table(scroll)
        self._build_workflow_buttons(scroll)
        self._build_detail_panel(scroll)

    # ── Header ────────────────────────────────────────────────────

    def _build_header(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        bar.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            bar,
            text="AI Content Planner",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w",
        )
        title.pack(side="left")

        badge = under_construction_badge(
            bar, self.theme, text="Needs Claude API key for AI generation"
        )
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
            command=self._load_plans,
        )
        refresh_btn.pack(side="right")

    # ── AI Generation Form ────────────────────────────────────────

    def _build_generate_form(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))

        header_row = ctk.CTkFrame(frame, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header_row,
            text="Generate Ideas with AI",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(side="left")

        ai_badge = under_construction_badge(
            header_row, self.theme, text="Requires Claude API key"
        )
        ai_badge.pack(side="left", padx=(8, 0))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(0, 15))

        # Niche
        ctk.CTkLabel(
            row,
            text="Niche:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left")

        self.niche_entry = ctk.CTkEntry(
            row, width=180, placeholder_text="e.g. Real Estate Investing"
        )
        self.niche_entry.pack(side="left", padx=(5, 15))

        # Number of ideas
        ctk.CTkLabel(
            row,
            text="Ideas:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left")

        self.ideas_var = ctk.StringVar(value="5")
        self.ideas_spinner = ctk.CTkEntry(row, width=50, textvariable=self.ideas_var)
        self.ideas_spinner.pack(side="left", padx=(5, 15))

        # Content type
        ctk.CTkLabel(
            row,
            text="Type:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(side="left")

        self.type_var = ctk.StringVar(value=self.CONTENT_TYPES[0])
        self.type_menu = ctk.CTkOptionMenu(
            row,
            values=self.CONTENT_TYPES,
            variable=self.type_var,
            width=130,
            fg_color=self.theme["button_bg"],
            button_color=self.theme["button_hover"],
            button_hover_color=self.theme["accent_hover"],
        )
        self.type_menu.pack(side="left", padx=(5, 15))

        # Generate button
        ctk.CTkButton(
            row,
            text="Generate Ideas",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=140,
            height=32,
            corner_radius=8,
            command=self._generate_ideas,
        ).pack(side="left")

    # ── Manual Plan Form ──────────────────────────────────────────

    def _build_manual_form(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            frame,
            text="Create Plan Manually",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=15, pady=(15, 5))

        form = ctk.CTkFrame(frame, fg_color="transparent")
        form.pack(fill="x", padx=15, pady=(0, 10))

        # Title
        ctk.CTkLabel(
            form, text="Title:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=0, column=0, sticky="w", pady=3)

        self.manual_title = ctk.CTkEntry(form, width=350, placeholder_text="Video title")
        self.manual_title.grid(row=0, column=1, padx=(5, 15), pady=3, sticky="w")

        # Keywords
        ctk.CTkLabel(
            form, text="Keywords:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=0, column=2, sticky="w", pady=3)

        self.manual_keywords = ctk.CTkEntry(
            form, width=250, placeholder_text="comma-separated keywords"
        )
        self.manual_keywords.grid(row=0, column=3, padx=(5, 0), pady=3, sticky="w")

        # Target date
        ctk.CTkLabel(
            form, text="Target Date:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=1, column=0, sticky="w", pady=3)

        self.manual_date = ctk.CTkEntry(
            form, width=150, placeholder_text="YYYY-MM-DD"
        )
        self.manual_date.grid(row=1, column=1, padx=(5, 15), pady=3, sticky="w")

        # Outline
        ctk.CTkLabel(
            form, text="Outline:",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).grid(row=2, column=0, sticky="nw", pady=3)

        self.manual_outline = ctk.CTkTextbox(
            form, width=620, height=80,
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
        )
        self.manual_outline.grid(row=2, column=1, columnspan=3, padx=(5, 0), pady=3, sticky="w")

        # Save button
        ctk.CTkButton(
            frame,
            text="Save Plan",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["success"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=120,
            height=32,
            corner_radius=8,
            command=self._save_manual_plan,
        ).pack(anchor="e", padx=15, pady=(0, 15))

    # ── Plans Table ───────────────────────────────────────────────

    def _build_plans_table(self, parent):
        table_frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        ctk.CTkLabel(
            table_frame,
            text="Content Plans",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=15, pady=(15, 5))

        cols = ("title", "niche", "keywords", "target_date", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)

        self.tree.heading("title", text="Title")
        self.tree.heading("niche", text="Niche")
        self.tree.heading("keywords", text="Keywords")
        self.tree.heading("target_date", text="Target Date")
        self.tree.heading("status", text="Status")

        self.tree.column("title", width=220)
        self.tree.column("niche", width=130)
        self.tree.column("keywords", width=180)
        self.tree.column("target_date", width=100)
        self.tree.column("status", width=90)

        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.tree.bind("<<TreeviewSelect>>", self._on_plan_selected)

    # ── Workflow Buttons ──────────────────────────────────────────

    def _build_workflow_buttons(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        for text, color, cmd in [
            ("Mark In Progress", self.theme["accent"], self._mark_in_progress),
            ("Mark Complete", self.theme["success"], self._mark_complete),
            ("Delete Plan", self.theme["error"], self._delete_plan),
        ]:
            ctk.CTkButton(
                row, text=text,
                font=(self.theme["font_family"], self.theme["font_size_body"]),
                fg_color=color,
                hover_color=self.theme["accent_hover"],
                text_color="#FFFFFF",
                width=140, height=32, corner_radius=8,
                command=cmd,
            ).pack(side="left", padx=(0, 10))

    # ── Detail Panel ──────────────────────────────────────────────

    def _build_detail_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=10)
        frame.pack(fill="both", expand=True, pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text="Plan Outline",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.detail_box = ctk.CTkTextbox(
            frame, height=120,
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_primary"],
            state="disabled",
        )
        self.detail_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # ── Data helpers ──────────────────────────────────────────────

    def _load_plans(self):
        """Fetch plans from the database and populate the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        plans = self.db.get_all_content_plans()
        for p in plans:
            self.tree.insert("", "end", iid=str(p["id"]), values=(
                p.get("title", ""),
                p.get("niche", ""),
                p.get("keywords", ""),
                p.get("target_date", ""),
                p.get("status", "idea"),
            ))
        self._clear_detail()

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a plan from the table.")
            return None
        return int(sel[0])

    def _on_plan_selected(self, _event=None):
        plan_id = self._get_selected_id() if self.tree.selection() else None
        if plan_id is None:
            self._clear_detail()
            return
        plans = self.db.get_all_content_plans()
        plan = next((p for p in plans if p["id"] == plan_id), None)
        if plan:
            self.detail_box.configure(state="normal")
            self.detail_box.delete("1.0", "end")
            self.detail_box.insert("1.0", plan.get("outline", ""))
            self.detail_box.configure(state="disabled")

    def _clear_detail(self):
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        self.detail_box.configure(state="disabled")

    # ── Actions ───────────────────────────────────────────────────

    def _generate_ideas(self):
        """Placeholder: store a generated plan (AI integration pending)."""
        niche = self.niche_entry.get().strip()
        if not niche:
            messagebox.showwarning("Missing Niche", "Enter a niche before generating ideas.")
            return

        count = max(1, min(20, int(self.ideas_var.get() or 5)))
        content_type = self.type_var.get()

        for i in range(1, count + 1):
            title = f"[AI Placeholder] {content_type}: {niche} idea #{i}"
            outline = f"Auto-generated {content_type.lower()} outline for '{niche}' — replace with Claude API output."
            self.db.add_content_plan(
                title=title, niche=niche, outline=outline,
                keywords=niche, target_date=None, status="idea",
            )

        messagebox.showinfo("Ideas Generated", f"{count} placeholder idea(s) saved. Connect the Claude API for real suggestions.")
        self._load_plans()

    def _save_manual_plan(self):
        title = self.manual_title.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a plan title.")
            return

        outline = self.manual_outline.get("1.0", "end").strip()
        keywords = self.manual_keywords.get().strip()
        target_date = self.manual_date.get().strip() or None

        self.db.add_content_plan(
            title=title, niche="", outline=outline,
            keywords=keywords, target_date=target_date, status="idea",
        )

        # Clear form fields
        self.manual_title.delete(0, "end")
        self.manual_outline.delete("1.0", "end")
        self.manual_keywords.delete(0, "end")
        self.manual_date.delete(0, "end")

        messagebox.showinfo("Saved", f"Plan '{title}' saved successfully.")
        self._load_plans()

    def _mark_in_progress(self):
        plan_id = self._get_selected_id()
        if plan_id is not None:
            self.db.update_content_plan_status(plan_id, "in_progress")
            self._load_plans()

    def _mark_complete(self):
        plan_id = self._get_selected_id()
        if plan_id is not None:
            self.db.update_content_plan_status(plan_id, "complete")
            self._load_plans()

    def _delete_plan(self):
        plan_id = self._get_selected_id()
        if plan_id is None:
            return
        if messagebox.askyesno("Confirm Delete", "Delete this content plan?"):
            self.db.delete_content_plan(plan_id)
            self._load_plans()
