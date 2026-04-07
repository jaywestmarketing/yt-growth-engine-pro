# -*- coding: utf-8 -*-
"""
RealE Tube - SEO Score Card Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from database.db import DatabaseManager
import json, re


class SEOScorecardTab:
    """Fully functional SEO scoring tab for video metadata analysis."""

    POWER_WORDS = {
        "how", "best", "top", "ultimate", "guide", "review", "vs",
        "new", "free", "easy", "proven", "secret", "amazing", "epic",
    }

    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()
        self.videos = []
        self.video_map = {}
        self.current_scores = {}

        self.create_ui()
        self.load_videos()

    # ── UI Construction ──────────────────────────────────────────

    def create_ui(self):
        """Build the full SEO Score Card interface."""
        main_frame = ctk.CTkScrollableFrame(
            self.parent, fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header(main_frame)
        self._create_video_selector(main_frame)
        self._create_manual_input(main_frame)
        self._create_score_display(main_frame)
        self._create_recommendations(main_frame)
        self._create_save_section(main_frame)
        self._create_history(main_frame)

    def _create_header(self, parent):
        """Header row with title and refresh button."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            header,
            text="SEO Score Card",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            width=90,
            command=self._on_refresh,
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
        ).pack(side="right")

    def _create_video_selector(self, parent):
        """Dropdown to pick an existing video plus Analyze button."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            inner,
            text="Select Video",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w")

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x", pady=(6, 0))

        self.video_dropdown = ctk.CTkComboBox(
            row,
            values=["-- manual input --"],
            width=500,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            border_color=self.theme["bg_tertiary"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            dropdown_fg_color=self.theme["bg_secondary"],
            command=self._on_video_selected,
        )
        self.video_dropdown.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            row,
            text="Analyze",
            width=100,
            command=self._on_analyze,
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
        ).pack(side="right", padx=(10, 0))

    def _create_manual_input(self, parent):
        """Manual title / description / tags entry."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            inner, text="Manual Input",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", pady=(0, 6))

        # Title
        ctk.CTkLabel(
            inner, text="Title",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(
            inner, placeholder_text="Enter video title...",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            border_color=self.theme["bg_tertiary"],
        )
        self.title_entry.pack(fill="x", pady=(2, 8))

        # Description
        ctk.CTkLabel(
            inner, text="Description",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(anchor="w")
        self.desc_textbox = ctk.CTkTextbox(
            inner, height=100,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
        )
        self.desc_textbox.pack(fill="x", pady=(2, 8))

        # Tags
        ctk.CTkLabel(
            inner, text="Tags (comma-separated)",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
        ).pack(anchor="w")
        self.tags_entry = ctk.CTkEntry(
            inner, placeholder_text="tag1, tag2, long tail keyword, ...",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            border_color=self.theme["bg_tertiary"],
        )
        self.tags_entry.pack(fill="x", pady=(2, 0))

    def _create_score_display(self, parent):
        """Four score cards in a row."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 12))
        frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.score_labels = {}
        headings = [
            ("Title Score", "title"),
            ("Description Score", "desc"),
            ("Tags Score", "tags"),
            ("Overall Score", "overall"),
        ]
        for col, (label_text, key) in enumerate(headings):
            card = ctk.CTkFrame(frame, fg_color=self.theme["bg_secondary"], corner_radius=8)
            card.grid(row=0, column=col, padx=4, sticky="nsew")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=14, pady=14)

            ctk.CTkLabel(
                inner, text=label_text,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_secondary"],
            ).pack()

            score_lbl = ctk.CTkLabel(
                inner, text="--",
                font=(self.theme["font_family"], 28, "bold"),
                text_color=self.theme["text_primary"],
            )
            score_lbl.pack(pady=(4, 0))
            self.score_labels[key] = score_lbl

    def _create_recommendations(self, parent):
        """Textbox showing specific improvement suggestions."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            inner, text="Recommendations",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", pady=(0, 6))

        self.reco_textbox = ctk.CTkTextbox(
            inner, height=150,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["bg_tertiary"],
            state="disabled",
        )
        self.reco_textbox.pack(fill="x")

    def _create_save_section(self, parent):
        """Save Audit button (requires a video from the dropdown)."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 16))

        self.save_btn = ctk.CTkButton(
            frame, text="Save Audit", width=140,
            command=self._on_save_audit,
            fg_color=self.theme["success"],
            hover_color=self.theme["accent_hover"],
            state="disabled",
        )
        self.save_btn.pack(side="right")

        self.save_status_lbl = ctk.CTkLabel(
            frame, text="",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"],
        )
        self.save_status_lbl.pack(side="right", padx=(0, 12))

    def _create_history(self, parent):
        """Past audits table."""
        frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"], corner_radius=8)
        frame.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            inner, text="Audit History",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
        ).pack(anchor="w", pady=(0, 6))

        self.history_container = ctk.CTkFrame(inner, fg_color="transparent")
        self.history_container.pack(fill="x")

        self._refresh_history()

    # ── Data Loading ─────────────────────────────────────────────

    def load_videos(self):
        """Fetch videos from the database and populate dropdown."""
        try:
            self.videos = self.db.get_all_videos()
        except Exception:
            self.videos = []
        self.video_map = {}
        labels = ["-- manual input --"]
        for v in self.videos:
            title = v.get("title_used") or v.get("title") or f"Video {v['id']}"
            display = f"[{v['id']}] {title[:80]}"
            labels.append(display)
            self.video_map[display] = v
        self.video_dropdown.configure(values=labels)
        self.video_dropdown.set(labels[0])

    # ── Event Handlers ───────────────────────────────────────────

    def _on_refresh(self):
        self.load_videos()
        self._refresh_history()

    def _on_video_selected(self, choice):
        """Populate manual fields from a selected video."""
        if choice == "-- manual input --":
            return
        video = self.video_map.get(choice)
        if not video:
            return
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, video.get("title_used") or video.get("title") or "")
        self.desc_textbox.delete("1.0", "end")
        self.desc_textbox.insert("1.0", video.get("description") or "")
        self.tags_entry.delete(0, "end")
        tags_raw = video.get("tags") or ""
        if tags_raw.startswith("["):
            try:
                tags_raw = ", ".join(json.loads(tags_raw))
            except (json.JSONDecodeError, TypeError):
                pass
        self.tags_entry.insert(0, tags_raw)

    def _on_analyze(self):
        """Run scoring on current manual input fields."""
        title = self.title_entry.get().strip()
        desc = self.desc_textbox.get("1.0", "end-1c").strip()
        tags_str = self.tags_entry.get().strip()

        title_score, title_recos = self._score_title(title)
        desc_score, desc_recos = self._score_description(desc)
        tags_score, tags_recos = self._score_tags(tags_str)

        overall = round(title_score * 0.35 + desc_score * 0.35 + tags_score * 0.30)

        self.current_scores = {
            "title": title_score,
            "desc": desc_score,
            "tags": tags_score,
            "overall": overall,
        }

        for key, val in self.current_scores.items():
            color = self._color_for_score(val)
            self.score_labels[key].configure(text=str(val), text_color=color)

        all_recos = title_recos + desc_recos + tags_recos
        if not all_recos:
            all_recos = ["Great job! Your metadata looks well-optimized."]

        self.reco_textbox.configure(state="normal")
        self.reco_textbox.delete("1.0", "end")
        self.reco_textbox.insert("1.0", "\n".join(f"  - {r}" for r in all_recos))
        self.reco_textbox.configure(state="disabled")

        # Enable save only when a video is selected from the dropdown
        selected = self.video_dropdown.get()
        if selected != "-- manual input --" and selected in self.video_map:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")
        self.save_status_lbl.configure(text="")

    def _on_save_audit(self):
        """Persist the current audit to the database."""
        selected = self.video_dropdown.get()
        video = self.video_map.get(selected)
        if not video or not self.current_scores:
            return

        recos_text = self.reco_textbox.get("1.0", "end-1c").strip()
        try:
            self.db.add_seo_audit(
                video_id=video["id"],
                title_score=self.current_scores["title"],
                desc_score=self.current_scores["desc"],
                tags_score=self.current_scores["tags"],
                overall_score=self.current_scores["overall"],
                recommendations=recos_text,
            )
            self.save_status_lbl.configure(
                text="Audit saved successfully.",
                text_color=self.theme["success"],
            )
            self._refresh_history()
        except Exception as exc:
            self.save_status_lbl.configure(
                text=f"Save failed: {exc}",
                text_color=self.theme["error"],
            )

    # ── Scoring Logic ────────────────────────────────────────────

    def _score_title(self, title: str):
        score = 0
        recos = []
        length = len(title)

        # 25 pts: ideal length 40-70
        if 40 <= length <= 70:
            score += 25
        elif 20 <= length < 40 or 70 < length <= 90:
            score += 12
            recos.append(f"Title length is {length} chars; aim for 40-70 for best CTR.")
        else:
            recos.append(f"Title length is {length} chars; aim for 40-70 for best CTR.")

        # 20 pts: contains a number
        if re.search(r"\d", title):
            score += 20
        else:
            recos.append("Add a number to your title (e.g. '5 Tips', '2024') to boost clicks.")

        # 20 pts: power words
        words_lower = set(re.findall(r"[a-z]+", title.lower()))
        if words_lower & self.POWER_WORDS:
            score += 20
        else:
            recos.append("Use a power word (how, best, top, ultimate, guide, review, vs, new).")

        # 15 pts: first word capitalised
        if title and title[0].isupper():
            score += 15
        else:
            recos.append("Capitalise the first word of your title.")

        # 20 pts: not ALL CAPS
        if title and title != title.upper():
            score += 20
        elif title:
            recos.append("Avoid writing the entire title in ALL CAPS.")

        return min(score, 100), recos

    def _score_description(self, desc: str):
        score = 0
        recos = []
        length = len(desc)

        # 30 pts: >500 chars
        if length > 500:
            score += 30
        elif length > 300:
            score += 15
            recos.append(f"Description is {length} chars; aim for 500+ for better SEO.")
        else:
            recos.append(f"Description is only {length} chars; aim for 500+ for better SEO.")

        # 20 pts: contains link
        if re.search(r"https?://", desc):
            score += 20
        else:
            recos.append("Include at least one link (website, social, affiliate) in the description.")

        # 15 pts: timestamps
        if re.search(r"\d+:\d+", desc):
            score += 15
        else:
            recos.append("Add timestamps (e.g. 0:00, 2:15) to improve viewer retention.")

        # 20 pts: >200 chars (baseline readability)
        if length > 200:
            score += 20
        else:
            recos.append("Write at least 200 characters to give YouTube enough context.")

        # 15 pts: paragraphs
        if "\n\n" in desc:
            score += 15
        else:
            recos.append("Break your description into paragraphs for readability.")

        return min(score, 100), recos

    def _score_tags(self, tags_str: str):
        score = 0
        recos = []
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        count = len(tags)

        # 30 pts: 5-15 tags
        if 5 <= count <= 15:
            score += 30
        elif count > 0:
            score += 10
            recos.append(f"You have {count} tags; 5-15 is the sweet spot.")
        else:
            recos.append("Add tags! Aim for 5-15 relevant tags.")

        # 25 pts: long-tail (3+ words)
        long_tail = [t for t in tags if len(t.split()) >= 3]
        if long_tail:
            score += 25
        else:
            recos.append("Include at least one long-tail tag (3+ words) for niche discoverability.")

        # 25 pts: no duplicates
        lower_tags = [t.lower() for t in tags]
        if len(lower_tags) == len(set(lower_tags)):
            score += 25
        else:
            dupes = set(t for t in lower_tags if lower_tags.count(t) > 1)
            recos.append(f"Remove duplicate tags: {', '.join(dupes)}.")

        # 20 pts: total chars reasonable (50-500)
        total_chars = sum(len(t) for t in tags)
        if 50 <= total_chars <= 500:
            score += 20
        elif total_chars > 0:
            score += 8
            recos.append("Total tag character count should be between 50-500 for best results.")
        else:
            recos.append("Add tags with a combined length of 50-500 characters.")

        return min(score, 100), recos

    # ── History ──────────────────────────────────────────────────

    def _refresh_history(self):
        """Reload audit history rows."""
        for child in self.history_container.winfo_children():
            child.destroy()

        try:
            audits = self.db.get_seo_audits()
        except Exception:
            audits = []

        if not audits:
            ctk.CTkLabel(
                self.history_container,
                text="No audits recorded yet.",
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(anchor="w")
            return

        # Column headers
        hdr = ctk.CTkFrame(self.history_container, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))
        for col_text, w in [("Video", 260), ("Title", 50), ("Desc", 50),
                            ("Tags", 50), ("Overall", 60), ("Date", 120)]:
            ctk.CTkLabel(
                hdr, text=col_text, width=w,
                font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                text_color=self.theme["text_secondary"],
            ).pack(side="left", padx=2)

        for audit in audits[:15]:
            row = ctk.CTkFrame(self.history_container, fg_color=self.theme["bg_tertiary"],
                               corner_radius=4, height=30)
            row.pack(fill="x", pady=1)
            video_label = audit.get("title_used") or f"Video {audit.get('video_id', '?')}"
            ts = str(audit.get("created_at", ""))[:16]
            overall = audit.get("overall_score", 0)
            color = self._color_for_score(overall)
            for text, w in [(video_label[:35], 260),
                            (str(audit.get("title_score", "--")), 50),
                            (str(audit.get("desc_score", "--")), 50),
                            (str(audit.get("tags_score", "--")), 50)]:
                ctk.CTkLabel(
                    row, text=text, width=w,
                    font=(self.theme["font_family"], self.theme["font_size_small"]),
                    text_color=self.theme["text_primary"],
                ).pack(side="left", padx=2)
            ctk.CTkLabel(
                row, text=str(overall), width=60,
                font=(self.theme["font_family"], self.theme["font_size_small"], "bold"),
                text_color=color,
            ).pack(side="left", padx=2)
            ctk.CTkLabel(
                row, text=ts, width=120,
                font=(self.theme["font_family"], self.theme["font_size_small"]),
                text_color=self.theme["text_tertiary"],
            ).pack(side="left", padx=2)

    # ── Helpers ──────────────────────────────────────────────────

    def _color_for_score(self, score):
        """Return a theme colour based on score bracket."""
        if score >= 75:
            return self.theme["success"]
        elif score >= 50:
            return self.theme["warning"]
        return self.theme["error"]
