# -*- coding: utf-8 -*-
"""
RealE Tube - Manual Comment Bot Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk
import threading

class ManualCommentTab:
    def __init__(self, parent, theme):
        """Initialize manual comment bot tab"""
        self.parent = parent
        self.theme = theme
        self.standalone_bot = None
        self.found_videos = []
        self.selected_videos = set()
        
        self.create_ui()
    
    def set_bot(self, bot):
        """Set the standalone comment bot instance"""
        self.standalone_bot = bot
    
    def create_ui(self):
        """Create the manual comment tab UI"""
        # Main container with scrollbar
        main_container = ctk.CTkFrame(
            self.parent,
            fg_color=self.theme["bg_primary"]
        )
        main_container.pack(fill="both", expand=True)
        
        # Scroll frame
        scroll_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color=self.theme["bg_primary"]
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            scroll_frame,
            text="Manual Comment Bot",
            font=(self.theme["font_family"], 24, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=(0, 20))
        
        # Method 1: Find Similar Videos
        self.create_similar_videos_section(scroll_frame)
        
        # Method 2: Browse Channel Videos
        self.create_channel_browser_section(scroll_frame)
        
        # Comment Configuration
        self.create_comment_config_section(scroll_frame)
        
        # Video List & Actions
        self.create_video_list_section(scroll_frame)
    
    def create_similar_videos_section(self, parent):
        """Create section for finding similar videos"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="Method 1: Find Similar Videos",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(padx=20, pady=(20, 10))
        
        # Description
        desc = ctk.CTkLabel(
            frame,
            text="Paste a YouTube video URL to find similar videos for commenting",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_secondary"]
        )
        desc.pack(padx=20, pady=(0, 15))
        
        # URL input
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.url_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="https://youtube.com/watch?v=...",
            height=40,
            font=(self.theme["font_family"], 14)
        )
        self.url_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            input_frame,
            text="Find Similar",
            command=self.find_similar_videos,
            height=40,
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"]
        )
        search_btn.pack(side="right")
        
        # Max results slider
        slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            slider_frame,
            text="Max Results:",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=(0, 10))
        
        self.max_results_slider = ctk.CTkSlider(
            slider_frame,
            from_=10,
            to=50,
            number_of_steps=8
        )
        self.max_results_slider.set(20)
        self.max_results_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.max_results_label = ctk.CTkLabel(
            slider_frame,
            text="20",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_primary"]
        )
        self.max_results_label.pack(side="right")
        
        self.max_results_slider.configure(command=lambda v: self.max_results_label.configure(text=str(int(v))))
    
    def create_channel_browser_section(self, parent):
        """Create section for browsing channel videos"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="Method 2: Browse Channel Videos",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(padx=20, pady=(20, 10))
        
        # Description
        desc = ctk.CTkLabel(
            frame,
            text="Enter a YouTube channel URL to browse their videos",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_secondary"]
        )
        desc.pack(padx=20, pady=(0, 15))
        
        # Channel URL input
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.channel_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="https://youtube.com/@channelname or https://youtube.com/channel/UC...",
            height=40,
            font=(self.theme["font_family"], 14)
        )
        self.channel_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            input_frame,
            text="Browse Channel",
            command=self.browse_channel,
            height=40,
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"]
        )
        browse_btn.pack(side="right")
    
    def create_comment_config_section(self, parent):
        """Create comment configuration section"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="Comment Configuration",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(padx=20, pady=(20, 15))
        
        # Comment style
        style_frame = ctk.CTkFrame(frame, fg_color="transparent")
        style_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            style_frame,
            text="Comment Style:",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=(0, 10))
        
        self.comment_style = ctk.CTkOptionMenu(
            style_frame,
            values=["helpful", "question", "appreciation", "engaging"],
            width=150
        )
        self.comment_style.set("helpful")
        self.comment_style.pack(side="left")
        
        # Delay between comments
        delay_frame = ctk.CTkFrame(frame, fg_color="transparent")
        delay_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            delay_frame,
            text="Delay Between Comments (seconds):",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=(0, 10))
        
        self.delay_slider = ctk.CTkSlider(
            delay_frame,
            from_=30,
            to=180,
            number_of_steps=15
        )
        self.delay_slider.set(60)
        self.delay_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.delay_label = ctk.CTkLabel(
            delay_frame,
            text="60s",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_primary"]
        )
        self.delay_label.pack(side="right")
        
        self.delay_slider.configure(command=lambda v: self.delay_label.configure(text=f"{int(v)}s"))
        
        # Max comments per batch
        max_frame = ctk.CTkFrame(frame, fg_color="transparent")
        max_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            max_frame,
            text="Max Comments Per Batch:",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=(0, 10))
        
        self.max_comments_slider = ctk.CTkSlider(
            max_frame,
            from_=1,
            to=20,
            number_of_steps=19
        )
        self.max_comments_slider.set(5)
        self.max_comments_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.max_comments_label = ctk.CTkLabel(
            max_frame,
            text="5",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_primary"]
        )
        self.max_comments_label.pack(side="right")
        
        self.max_comments_slider.configure(command=lambda v: self.max_comments_label.configure(text=str(int(v))))
    
    def create_video_list_section(self, parent):
        """Create video list and action buttons"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="both", expand=True)
        
        # Title with count
        title_frame = ctk.CTkFrame(frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        ctk.CTkLabel(
            title_frame,
            text="Found Videos",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left")
        
        self.video_count_label = ctk.CTkLabel(
            title_frame,
            text="0 videos",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_secondary"]
        )
        self.video_count_label.pack(side="left", padx=(10, 0))
        
        # Video table
        table_frame = ctk.CTkFrame(frame, fg_color=self.theme["bg_tertiary"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Create treeview
        columns = ("select", "title", "likes", "video_id")
        self.video_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10,
            selectmode="extended"
        )
        
        # Column headers
        self.video_tree.heading("select", text="✓")
        self.video_tree.heading("title", text="Title")
        self.video_tree.heading("likes", text="Likes")
        self.video_tree.heading("video_id", text="Video ID")
        
        # Column widths
        self.video_tree.column("select", width=30, anchor="center")
        self.video_tree.column("title", width=400)
        self.video_tree.column("likes", width=80)
        self.video_tree.column("video_id", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.video_tree.yview)
        self.video_tree.configure(yscrollcommand=scrollbar.set)
        
        self.video_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.video_tree.bind('<ButtonRelease-1>', self.on_video_select)
        
        # Action buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        select_all_btn = ctk.CTkButton(
            button_frame,
            text="Select All",
            command=self.select_all_videos,
            width=120
        )
        select_all_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Selection",
            command=self.clear_selection,
            width=120
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        self.comment_btn = ctk.CTkButton(
            button_frame,
            text="Post Comments on Selected",
            command=self.post_comments,
            fg_color=self.theme["success"],
            hover_color=self.theme["accent_hover"],
            width=200
        )
        self.comment_btn.pack(side="right")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            frame,
            text="",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_secondary"]
        )
        self.status_label.pack(padx=20, pady=(0, 20))
    
    def find_similar_videos(self):
        """Find similar videos based on URL"""
        url = self.url_input.get().strip()
        
        if not url:
            self.status_label.configure(text="Please enter a YouTube URL", text_color=self.theme["error"])
            return
        
        if not self.standalone_bot:
            self.status_label.configure(text="Comment bot not initialized", text_color=self.theme["error"])
            return
        
        self.status_label.configure(text="Analyzing video...", text_color=self.theme["text_secondary"])
        self.comment_btn.configure(state="disabled")
        
        # Run in thread
        threading.Thread(
            target=self._find_similar_thread,
            args=(url, int(self.max_results_slider.get())),
            daemon=True
        ).start()
    
    def _find_similar_thread(self, url, max_results):
        """Thread for finding similar videos"""
        videos = self.standalone_bot.analyze_video_and_find_similar(url, max_results)
        self.found_videos = videos
        self._update_video_list()
    
    def browse_channel(self):
        """Browse channel videos"""
        url = self.channel_input.get().strip()
        
        if not url:
            self.status_label.configure(text="Please enter a channel URL", text_color=self.theme["error"])
            return
        
        if not self.standalone_bot:
            self.status_label.configure(text="Comment bot not initialized", text_color=self.theme["error"])
            return
        
        self.status_label.configure(text="Loading channel videos...", text_color=self.theme["text_secondary"])
        self.comment_btn.configure(state="disabled")
        
        # Run in thread
        threading.Thread(
            target=self._browse_channel_thread,
            args=(url,),
            daemon=True
        ).start()
    
    def _browse_channel_thread(self, url):
        """Thread for browsing channel"""
        videos = self.standalone_bot.get_channel_videos(url, max_results=50)
        self.found_videos = videos
        self._update_video_list()
    
    def _update_video_list(self):
        """Update the video list table"""
        # Clear existing
        for item in self.video_tree.get_children():
            self.video_tree.delete(item)
        
        # Add videos
        for video in self.found_videos:
            likes = video.get('likes', 'N/A')
            self.video_tree.insert("", "end", values=(
                "",
                video.get('title', 'Unknown')[:60] + "...",
                likes,
                video['video_id']
            ))
        
        # Update count
        self.video_count_label.configure(text=f"{len(self.found_videos)} videos")
        self.status_label.configure(text=f"Found {len(self.found_videos)} videos", text_color=self.theme["success"])
        self.comment_btn.configure(state="normal")
    
    def on_video_select(self, event):
        """Handle video selection"""
        selection = self.video_tree.selection()
        self.selected_videos = set(selection)
    
    def select_all_videos(self):
        """Select all videos"""
        for item in self.video_tree.get_children():
            self.video_tree.selection_add(item)
        self.selected_videos = set(self.video_tree.get_children())
    
    def clear_selection(self):
        """Clear all selections"""
        self.video_tree.selection_remove(*self.video_tree.get_children())
        self.selected_videos.clear()
    
    def post_comments(self):
        """Post comments on selected videos"""
        if not self.selected_videos:
            self.status_label.configure(text="Please select videos to comment on", text_color=self.theme["error"])
            return
        
        if not self.standalone_bot:
            self.status_label.configure(text="Comment bot not initialized", text_color=self.theme["error"])
            return
        
        # Get selected video IDs
        video_ids = []
        for item_id in self.selected_videos:
            values = self.video_tree.item(item_id)['values']
            video_ids.append(values[3])  # video_id is 4th column
        
        # Get settings
        style = self.comment_style.get()
        delay = int(self.delay_slider.get())
        max_comments = int(self.max_comments_slider.get())
        
        self.status_label.configure(
            text=f"Posting {min(len(video_ids), max_comments)} comments with {delay}s delay...",
            text_color=self.theme["text_secondary"]
        )
        self.comment_btn.configure(state="disabled")
        
        # Run in thread
        threading.Thread(
            target=self._post_comments_thread,
            args=(video_ids, style, delay, max_comments),
            daemon=True
        ).start()
    
    def _post_comments_thread(self, video_ids, style, delay, max_comments):
        """Thread for posting comments"""
        results = self.standalone_bot.comment_on_videos(
            video_ids=video_ids,
            comment_style=style,
            delay_seconds=delay,
            max_comments=max_comments
        )
        
        # Update UI
        self.status_label.configure(
            text=f"✓ Posted {results['success']} comments, {results['failed']} failed, {results['skipped']} skipped",
            text_color=self.theme["success"]
        )
        self.comment_btn.configure(state="normal")
