"""
RealE Tube - Analytics Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk

class AnalyticsTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        
        self.create_analytics()
    
    def create_analytics(self):
        """Create analytics layout"""
        # Main container
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Overall stats
        self.create_overall_stats(main_frame)
        
        # Performance charts section
        self.create_charts_section(main_frame)
        
        # Top keywords section
        self.create_keywords_section(main_frame)
    
    def create_overall_stats(self, parent):
        """Create overall statistics section"""
        stats_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title = ctk.CTkLabel(
            stats_frame,
            text="Overall Performance",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title.pack(fill="x", padx=20, pady=(20, 15))
        
        # Stats grid
        stats_container = ctk.CTkFrame(
            stats_frame,
            fg_color="transparent"
        )
        stats_container.pack(fill="x", padx=20, pady=(0, 20))
        stats_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Get real stats from database
        try:
            from database.db import DatabaseManager
            db = DatabaseManager()
            stats = db.get_statistics()
            db.close()
            
            success_rate = f"{stats['success_rate']:.1f}%"
            avg_attempts = f"{stats['avg_attempts']:.1f}"
            total_videos = sum(stats['by_status'].values())
            
        except Exception as e:
            print(f"Error loading stats: {e}")
            success_rate = "0%"
            avg_attempts = "0.0"
            total_videos = 0
        
        # Success rate
        self.create_metric_card(
            stats_container,
            "Success Rate",
            success_rate,
            "Videos meeting performance thresholds",
            self.theme["success"],
            0
        )
        
        # Average attempts
        self.create_metric_card(
            stats_container,
            "Avg. Attempts",
            avg_attempts,
            "Average retries to success",
            self.theme["accent"],
            1
        )
        
        # Total videos
        self.create_metric_card(
            stats_container,
            "Total Videos",
            str(total_videos),
            "Videos processed all-time",
            self.theme["text_primary"],
            2
        )
    
    def create_metric_card(self, parent, title, value, description, color, column):
        """Create individual metric card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_tertiary"],
            corner_radius=8
        )
        card.grid(row=0, column=column, padx=10, sticky="ew")
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(self.theme["font_family"], 36, "bold"),
            text_color=color
        )
        value_label.pack(pady=(20, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_secondary"]
        )
        title_label.pack(pady=(0, 5))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"]
        )
        desc_label.pack(pady=(0, 20))
    
    def create_charts_section(self, parent):
        """Create performance charts section"""
        charts_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        charts_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Title
        title = ctk.CTkLabel(
            charts_frame,
            text="Performance Over Time",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title.pack(fill="x", padx=20, pady=(20, 15))
        
        # Chart placeholder
        chart_container = ctk.CTkFrame(
            charts_frame,
            fg_color=self.theme["bg_tertiary"],
            corner_radius=8,
            height=300
        )
        chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        chart_container.pack_propagate(False)
        
        # Placeholder text
        placeholder = ctk.CTkLabel(
            chart_container,
            text="📊 Chart visualization will be implemented here\n\nTracking:\n• Upload success rate over time\n• Average views per video\n• CTR and engagement trends",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_tertiary"],
            justify="center"
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    def create_keywords_section(self, parent):
        """Create top keywords section"""
        keywords_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        keywords_frame.pack(fill="x")
        
        # Title
        title = ctk.CTkLabel(
            keywords_frame,
            text="Best Performing Keywords",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title.pack(fill="x", padx=20, pady=(20, 15))
        
        # Keywords grid
        keywords_container = ctk.CTkFrame(
            keywords_frame,
            fg_color="transparent"
        )
        keywords_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Get real keywords from database
        try:
            from database.db import DatabaseManager
            db = DatabaseManager()
            top_keywords = db.get_top_keywords(limit=10)
            db.close()
            
            if top_keywords:
                for i, kw in enumerate(top_keywords):
                    self.create_keyword_item(
                        keywords_container,
                        i + 1,
                        kw['keyword'],
                        f"{kw['video_count']} videos",
                        f"avg {int(kw['avg_views'])} views"
                    )
            else:
                # No data yet
                placeholder = ctk.CTkLabel(
                    keywords_container,
                    text="No keyword data yet. Upload videos to see statistics.",
                    font=(self.theme["font_family"], self.theme["font_size_body"]),
                    text_color=self.theme["text_tertiary"]
                )
                placeholder.pack(pady=20)
        except Exception as e:
            print(f"Error loading keywords: {e}")
            placeholder = ctk.CTkLabel(
                keywords_container,
                text="Unable to load keyword statistics.",
                font=(self.theme["font_family"], self.theme["font_size_body"]),
                text_color=self.theme["text_tertiary"]
            )
            placeholder.pack(pady=20)
    
    def create_keyword_item(self, parent, rank, keyword, count, performance):
        """Create individual keyword item"""
        item_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_tertiary"],
            corner_radius=8
        )
        item_frame.pack(fill="x", pady=(0, 10))
        
        # Rank
        rank_label = ctk.CTkLabel(
            item_frame,
            text=f"#{rank}",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["accent"],
            width=50
        )
        rank_label.pack(side="left", padx=(15, 10), pady=15)
        
        # Keyword
        keyword_label = ctk.CTkLabel(
            item_frame,
            text=keyword,
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        keyword_label.pack(side="left", padx=(0, 20), pady=15)
        
        # Count
        count_label = ctk.CTkLabel(
            item_frame,
            text=count,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        count_label.pack(side="left", padx=(0, 20), pady=15)
        
        # Performance
        perf_label = ctk.CTkLabel(
            item_frame,
            text=performance,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["success"],
            anchor="e"
        )
        perf_label.pack(side="right", padx=15, pady=15)
