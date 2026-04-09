# -*- coding: utf-8 -*-
"""
RealE Tube - Post Timing Tab
Copyright (c) 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from gui.tooltip import under_construction_badge
from database.db import DatabaseManager
from datetime import datetime


class PostTimingTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        self.db = DatabaseManager()
        self._create_ui()

    def _create_ui(self):
        t = self.theme
        main = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            header, text="Best Times to Post",
            font=(t["font_family"], t["font_size_heading"], "bold"),
            text_color=t["text_primary"]
        ).pack(side="left")
        badge = under_construction_badge(header, t,
            text="Live competitor timing analysis requires YouTube API polling. "
                 "Currently shows analysis from your own upload history.")
        badge.pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            header, text="Analyze", width=100, height=32,
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"], hover_color=t["accent_hover"],
            text_color="#FFFFFF", corner_radius=8,
            command=self._analyze
        ).pack(side="right")

        # ── Your upload history analysis ─────────────────────────
        section = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        section.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            section, text="Your Upload Performance by Time",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"]
        ).pack(anchor="w", padx=16, pady=(16, 8))

        self._history_frame = ctk.CTkFrame(section, fg_color="transparent")
        self._history_frame.pack(fill="x", padx=16, pady=(0, 16))

        # ── Recommended posting times ────────────────────────────
        rec_section = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        rec_section.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            rec_section, text="Recommended Posting Times",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"]
        ).pack(anchor="w", padx=16, pady=(16, 8))
        self._rec_frame = ctk.CTkFrame(rec_section, fg_color="transparent")
        self._rec_frame.pack(fill="x", padx=16, pady=(0, 16))

        # ── Competitor timing section ────────────────────────────
        comp_section = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        comp_section.pack(fill="x", pady=(0, 15))
        row = ctk.CTkFrame(comp_section, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            row, text="Competitor Post Timing",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"]
        ).pack(side="left")
        badge2 = under_construction_badge(row, t,
            text="Requires competitor channels to be tracked in the Competitors tab. "
                 "Fetches publish times via YouTube API.")
        badge2.pack(side="left", padx=(8, 0))
        self._comp_frame = ctk.CTkFrame(comp_section, fg_color="transparent")
        self._comp_frame.pack(fill="x", padx=16, pady=(0, 16))

        # ── Day-of-week heatmap ──────────────────────────────────
        heat_section = ctk.CTkFrame(main, fg_color=t["bg_secondary"], corner_radius=10)
        heat_section.pack(fill="x")
        ctk.CTkLabel(
            heat_section, text="Day & Hour Heatmap",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"]
        ).pack(anchor="w", padx=16, pady=(16, 8))
        self._heatmap_frame = ctk.CTkFrame(heat_section, fg_color="transparent")
        self._heatmap_frame.pack(fill="x", padx=16, pady=(0, 16))

        self._analyze()

    def _analyze(self):
        """Analyze upload history and competitor data for best posting times."""
        t = self.theme
        # Clear frames
        for f in (self._history_frame, self._rec_frame, self._comp_frame, self._heatmap_frame):
            for w in f.winfo_children():
                w.destroy()

        # ── Analyze own uploads ──────────────────────────────────
        try:
            videos = self.db.get_all_videos()
        except Exception:
            videos = []

        hour_stats = {}  # hour -> {count, total_views}
        day_stats = {}   # day_name -> {count, total_views}
        day_hour_grid = {}  # (day_idx, hour) -> views

        for v in videos:
            date_str = v.get('upload_date') or v.get('created_at') or ''
            views = v.get('views') or 0
            if not date_str:
                continue
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except Exception:
                continue
            h = dt.hour
            d = dt.strftime('%A')
            d_idx = dt.weekday()

            hour_stats.setdefault(h, {'count': 0, 'total_views': 0})
            hour_stats[h]['count'] += 1
            hour_stats[h]['total_views'] += views

            day_stats.setdefault(d, {'count': 0, 'total_views': 0, 'idx': d_idx})
            day_stats[d]['count'] += 1
            day_stats[d]['total_views'] += views

            key = (d_idx, h)
            day_hour_grid[key] = day_hour_grid.get(key, 0) + views

        if hour_stats:
            # Show hour breakdown
            for h in sorted(hour_stats.keys()):
                s = hour_stats[h]
                avg = s['total_views'] // max(s['count'], 1)
                bar_w = min(max(avg // 5, 10), 300)
                row = ctk.CTkFrame(self._history_frame, fg_color="transparent")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=f"{h:02d}:00", width=50, anchor="w",
                    font=(t["font_family"], 11), text_color=t["text_secondary"]
                ).pack(side="left")
                ctk.CTkLabel(row, text=f"{s['count']} uploads, avg {avg} views", width=180, anchor="w",
                    font=(t["font_family"], 11), text_color=t["text_primary"]
                ).pack(side="left", padx=(5, 5))
                bar = ctk.CTkFrame(row, fg_color=t["accent"], height=14,
                    width=bar_w, corner_radius=3)
                bar.pack(side="left")

            # Best hours
            best_hours = sorted(hour_stats.items(),
                key=lambda x: x[1]['total_views'] // max(x[1]['count'], 1), reverse=True)[:3]
            best_days = sorted(day_stats.items(),
                key=lambda x: x[1]['total_views'] // max(x[1]['count'], 1), reverse=True)[:3]

            rec_text = "Based on your upload history:\n\n"
            rec_text += "Best hours:  " + ", ".join(
                f"{h:02d}:00 (avg {s['total_views']//max(s['count'],1)} views)"
                for h, s in best_hours) + "\n\n"
            rec_text += "Best days:  " + ", ".join(
                f"{d} (avg {s['total_views']//max(s['count'],1)} views)"
                for d, s in best_days)

            ctk.CTkLabel(self._rec_frame, text=rec_text,
                font=(t["font_family"], 12), text_color=t["success"],
                justify="left", anchor="w", wraplength=600
            ).pack(anchor="w")
        else:
            ctk.CTkLabel(self._history_frame,
                text="No upload data yet. Upload videos to see timing analysis.",
                font=(t["font_family"], 12), text_color=t["text_tertiary"]
            ).pack(pady=10)
            ctk.CTkLabel(self._rec_frame,
                text="General best times for YouTube:\n\n"
                     "Weekdays: 12:00-15:00 and 17:00-21:00\n"
                     "Weekends: 09:00-12:00\n\n"
                     "These vary by niche — your own data will provide better guidance.",
                font=(t["font_family"], 12), text_color=t["text_secondary"],
                justify="left", anchor="w", wraplength=600
            ).pack(anchor="w")

        # ── Competitor timing ────────────────────────────────────
        try:
            competitors = self.db.get_all_competitor_channels()
        except Exception:
            competitors = []

        if competitors:
            comp_hour_stats = {}
            for comp in competitors:
                try:
                    vids = self.db.get_competitor_videos(comp['id'], limit=100)
                    for cv in vids:
                        pub = cv.get('published_at', '')
                        if pub:
                            try:
                                dt = datetime.fromisoformat(pub.replace('Z', '+00:00'))
                                h = dt.hour
                                comp_hour_stats.setdefault(h, 0)
                                comp_hour_stats[h] += 1
                            except Exception:
                                pass
                except Exception:
                    pass

            if comp_hour_stats:
                ctk.CTkLabel(self._comp_frame,
                    text=f"Analyzed {sum(comp_hour_stats.values())} competitor videos across {len(competitors)} channels:",
                    font=(t["font_family"], 12), text_color=t["text_secondary"]
                ).pack(anchor="w", pady=(0, 5))
                top_hours = sorted(comp_hour_stats.items(), key=lambda x: x[1], reverse=True)[:5]
                ctk.CTkLabel(self._comp_frame,
                    text="Most common posting hours:  " + ", ".join(
                        f"{h:02d}:00 ({c} videos)" for h, c in top_hours),
                    font=(t["font_family"], 12, "bold"), text_color=t["accent"]
                ).pack(anchor="w")
            else:
                ctk.CTkLabel(self._comp_frame,
                    text="Track competitors and fetch their videos to see posting patterns.",
                    font=(t["font_family"], 12), text_color=t["text_tertiary"]
                ).pack(pady=10)
        else:
            ctk.CTkLabel(self._comp_frame,
                text="No competitors tracked yet. Add channels in the Competitors tab.",
                font=(t["font_family"], 12), text_color=t["text_tertiary"]
            ).pack(pady=10)

        # ── Day/hour heatmap ─────────────────────────────────────
        if day_hour_grid:
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            max_views = max(day_hour_grid.values()) if day_hour_grid else 1
            # Header row
            hdr = ctk.CTkFrame(self._heatmap_frame, fg_color="transparent")
            hdr.pack(fill="x")
            ctk.CTkLabel(hdr, text="", width=40).pack(side="left")
            for h in range(0, 24, 3):
                ctk.CTkLabel(hdr, text=f"{h:02d}", width=30,
                    font=(t["font_family"], 9), text_color=t["text_tertiary"]
                ).pack(side="left")
            for d_idx, d_name in enumerate(days):
                row = ctk.CTkFrame(self._heatmap_frame, fg_color="transparent")
                row.pack(fill="x")
                ctk.CTkLabel(row, text=d_name, width=40, anchor="w",
                    font=(t["font_family"], 10), text_color=t["text_secondary"]
                ).pack(side="left")
                for h in range(0, 24, 3):
                    total = sum(day_hour_grid.get((d_idx, h+off), 0) for off in range(3))
                    intensity = total / max(max_views, 1)
                    if intensity > 0.6:
                        color = t["success"]
                    elif intensity > 0.3:
                        color = t["warning"]
                    elif intensity > 0:
                        color = t["accent"]
                    else:
                        color = t["bg_tertiary"]
                    cell = ctk.CTkFrame(row, fg_color=color, width=28, height=18, corner_radius=3)
                    cell.pack(side="left", padx=1, pady=1)
                    cell.pack_propagate(False)
        else:
            ctk.CTkLabel(self._heatmap_frame,
                text="Upload more videos to see the day/hour heatmap.",
                font=(t["font_family"], 12), text_color=t["text_tertiary"]
            ).pack(pady=10)
