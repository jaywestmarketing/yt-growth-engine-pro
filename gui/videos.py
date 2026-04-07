"""
RealE Tube - Videos Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk

class VideosTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        
        self.create_videos_view()
    
    def create_videos_view(self):
        """Create videos table layout"""
        # Main container
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with filters
        self.create_header(main_frame)
        
        # Videos table
        self.create_table(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
    
    def create_header(self, parent):
        """Create header with filters"""
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
        
        # Filter dropdown
        filter_label = ctk.CTkLabel(
            header_frame,
            text="Filter:",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"]
        )
        filter_label.pack(side="left", padx=(40, 10), pady=15)
        
        self.filter_dropdown = ctk.CTkOptionMenu(
            header_frame,
            values=["All", "Uploaded", "Monitoring", "Success", "Retry", "Abandoned"],
            fg_color=self.theme["button_bg"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            width=150,
            command=self.filter_videos
        )
        self.filter_dropdown.set("All")
        self.filter_dropdown.pack(side="left", pady=15)
        
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
    
    def create_table(self, parent):
        """Create videos table"""
        # Table container
        table_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        table_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create treeview with custom styling
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure colors based on theme
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
        columns = ("Title", "Status", "Attempt", "Views", "CTR", "Engagement", "Uploaded")
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
        self.tree.heading("Title", text="Title")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Attempt", text="Attempt")
        self.tree.heading("Views", text="Views")
        self.tree.heading("CTR", text="CTR %")
        self.tree.heading("Engagement", text="Engagement %")
        self.tree.heading("Uploaded", text="Uploaded")
        
        self.tree.column("Title", width=300)
        self.tree.column("Status", width=100)
        self.tree.column("Attempt", width=80)
        self.tree.column("Views", width=80)
        self.tree.column("CTR", width=80)
        self.tree.column("Engagement", width=120)
        self.tree.column("Uploaded", width=150)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sample data (will be replaced with actual data)
        self.populate_sample_data()
    
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
        delete_button.pack(side="left")
    
    def populate_sample_data(self):
        """Populate table with real data from database"""
        try:
            from database.db import DatabaseManager
            db = DatabaseManager()
            
            # Get all videos
            videos = db.get_all_videos()
            db.close()
            
            if videos:
                for video in videos:
                    # Format data for display
                    title = video.get('title_used', 'Untitled')[:40] + "..."
                    status = video.get('status', 'unknown').title()
                    attempt = str(video.get('attempt_number', 1))
                    views = str(video.get('views', 0))
                    ctr = f"{video.get('ctr', 0):.1f}"
                    engagement = f"{video.get('engagement_rate', 0):.1f}"
                    upload_date = video.get('upload_date', video.get('created_at', ''))[:16] if video.get('upload_date') else 'Pending'
                    
                    self.tree.insert("", "end", values=(
                        title, status, attempt, views, ctr, engagement, upload_date
                    ))
            else:
                # No videos yet
                self.tree.insert("", "end", values=(
                    "No videos uploaded yet", "-", "-", "-", "-", "-", "-"
                ))
        
        except Exception as e:
            print(f"Error loading videos: {e}")
            self.tree.insert("", "end", values=(
                "Error loading data", "-", "-", "-", "-", "-", "-"
            ))
    
    def filter_videos(self, filter_value):
        """Filter videos by status"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Repopulate based on filter (will integrate with database later)
        self.populate_sample_data()
        
        self.app.dashboard_tab.add_log_entry(f"Filtered videos: {filter_value}", "INFO")
    
    def refresh_table(self):
        """Refresh video table"""
        # Clear and reload (will integrate with database later)
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.populate_sample_data()
        self.app.dashboard_tab.add_log_entry("Video table refreshed", "INFO")
    
    def retry_selected(self):
        """Retry selected video"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            video_title = item['values'][0]
            self.app.dashboard_tab.add_log_entry(f"Manual retry initiated: {video_title}", "WARNING")
        else:
            self.app.dashboard_tab.add_log_entry("No video selected for retry", "ERROR")
    
    def delete_selected(self):
        """Delete selected video"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            video_title = item['values'][0]
            self.tree.delete(selection[0])
            self.app.dashboard_tab.add_log_entry(f"Video deleted: {video_title}", "WARNING")
        else:
            self.app.dashboard_tab.add_log_entry("No video selected for deletion", "ERROR")
