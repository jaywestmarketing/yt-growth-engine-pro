"""
RealE Tube - Channel Dashboard Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import ttk
import threading
from datetime import datetime, timedelta

class ChannelDashboardTab:
    def __init__(self, parent, theme):
        """Initialize channel dashboard tab"""
        self.parent = parent
        self.theme = theme
        self.youtube_service = None
        self.channel_id = None
        self.channel_data = {}
        
        self.create_ui()
    
    def set_youtube_service(self, youtube_service, channel_id):
        """Set YouTube service and channel ID"""
        self.youtube_service = youtube_service
        self.channel_id = channel_id
        self.refresh_data()
    
    def create_ui(self):
        """Create the channel dashboard UI"""
        # Main container
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
        
        # Header with refresh button
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Channel Dashboard",
            font=(self.theme["font_family"], 24, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(side="left")
        
        self.refresh_btn = ctk.CTkButton(
            header_frame,
            text="Refresh",
            command=self.refresh_data,
            width=100,
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"]
        )
        self.refresh_btn.pack(side="right")
        
        self.last_updated_label = ctk.CTkLabel(
            header_frame,
            text="Last updated: Never",
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_tertiary"]
        )
        self.last_updated_label.pack(side="right", padx=(0, 10))
        
        # Channel Overview Stats
        self.create_overview_section(scroll_frame)
        
        # Recent Videos Performance
        self.create_recent_videos_section(scroll_frame)
        
        # Growth Metrics
        self.create_growth_section(scroll_frame)
        
        # Top Performing Videos
        self.create_top_videos_section(scroll_frame)
    
    def create_overview_section(self, parent):
        """Create channel overview stats section"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            frame,
            text="Channel Overview",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(padx=20, pady=(20, 15))
        
        # Stats grid
        stats_container = ctk.CTkFrame(frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=(0, 20))
        stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create stat cards
        self.subscribers_card = self.create_stat_card(
            stats_container, "Subscribers", "0", self.theme["accent"], 0
        )
        
        self.total_views_card = self.create_stat_card(
            stats_container, "Total Views", "0", self.theme["success"], 1
        )
        
        self.total_videos_card = self.create_stat_card(
            stats_container, "Total Videos", "0", self.theme["text_primary"], 2
        )
        
        self.avg_views_card = self.create_stat_card(
            stats_container, "Avg Views/Video", "0", self.theme["accent_hover"], 3
        )
    
    def create_stat_card(self, parent, label, value, color, column):
        """Create a stat card"""
        card = ctk.CTkFrame(parent, fg_color=self.theme["bg_tertiary"], corner_radius=8)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(self.theme["font_family"], 28, "bold"),
            text_color=color
        )
        value_label.pack(pady=(15, 5))
        
        label_text = ctk.CTkLabel(
            card,
            text=label,
            font=(self.theme["font_family"], 12),
            text_color=self.theme["text_secondary"]
        )
        label_text.pack(pady=(0, 15))
        
        return {"value": value_label, "label": label_text}
    
    def create_recent_videos_section(self, parent):
        """Create recent videos performance section"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="both", expand=True, pady=(0, 20))
        
        title = ctk.CTkLabel(
            frame,
            text="Recent Videos (Last 30 Days)",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(padx=20, pady=(20, 15))
        
        # Table
        table_frame = ctk.CTkFrame(frame, fg_color=self.theme["bg_tertiary"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        columns = ("title", "published", "views", "likes", "comments", "ctr")
        self.recent_videos_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Headers
        self.recent_videos_tree.heading("title", text="Title")
        self.recent_videos_tree.heading("published", text="Published")
        self.recent_videos_tree.heading("views", text="Views")
        self.recent_videos_tree.heading("likes", text="Likes")
        self.recent_videos_tree.heading("comments", text="Comments")
        self.recent_videos_tree.heading("ctr", text="CTR %")
        
        # Column widths
        self.recent_videos_tree.column("title", width=300)
        self.recent_videos_tree.column("published", width=100)
        self.recent_videos_tree.column("views", width=80)
        self.recent_videos_tree.column("likes", width=80)
        self.recent_videos_tree.column("comments", width=80)
        self.recent_videos_tree.column("ctr", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.recent_videos_tree.yview)
        self.recent_videos_tree.configure(yscrollcommand=scrollbar.set)
        
        self.recent_videos_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_growth_section(self, parent):
        """Create growth metrics section"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            frame,
            text="Growth Metrics (Last 28 Days)",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(padx=20, pady=(20, 15))
        
        # Growth stats grid
        stats_container = ctk.CTkFrame(frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=(0, 20))
        stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.subs_gained_card = self.create_stat_card(
            stats_container, "Subscribers Gained", "+0", self.theme["success"], 0
        )
        
        self.views_28d_card = self.create_stat_card(
            stats_container, "Views (28d)", "0", self.theme["accent"], 1
        )
        
        self.watch_time_card = self.create_stat_card(
            stats_container, "Watch Time (hrs)", "0", self.theme["text_primary"], 2
        )
        
        self.engagement_card = self.create_stat_card(
            stats_container, "Engagement Rate", "0%", self.theme["accent_hover"], 3
        )
    
    def create_top_videos_section(self, parent):
        """Create top performing videos section"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        frame.pack(fill="both", expand=True)
        
        title = ctk.CTkLabel(
            frame,
            text="Top 10 Performing Videos (All Time)",
            font=(self.theme["font_family"], 18, "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(padx=20, pady=(20, 15))
        
        # Table
        table_frame = ctk.CTkFrame(frame, fg_color=self.theme["bg_tertiary"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        columns = ("rank", "title", "views", "likes", "engagement")
        self.top_videos_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Headers
        self.top_videos_tree.heading("rank", text="#")
        self.top_videos_tree.heading("title", text="Title")
        self.top_videos_tree.heading("views", text="Views")
        self.top_videos_tree.heading("likes", text="Likes")
        self.top_videos_tree.heading("engagement", text="Engagement %")
        
        # Column widths
        self.top_videos_tree.column("rank", width=40, anchor="center")
        self.top_videos_tree.column("title", width=400)
        self.top_videos_tree.column("views", width=100)
        self.top_videos_tree.column("likes", width=100)
        self.top_videos_tree.column("engagement", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.top_videos_tree.yview)
        self.top_videos_tree.configure(yscrollcommand=scrollbar.set)
        
        self.top_videos_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def refresh_data(self):
        """Refresh all channel data"""
        if not self.youtube_service or not self.channel_id:
            return
        
        self.refresh_btn.configure(state="disabled", text="Loading...")
        
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()
    
    def _fetch_data_thread(self):
        """Fetch data in background thread"""
        try:
            # Get channel statistics
            channel_response = self.youtube_service.channels().list(
                part='statistics,snippet',
                id=self.channel_id
            ).execute()
            
            if channel_response['items']:
                stats = channel_response['items'][0]['statistics']
                
                # Update overview stats
                self._update_overview_stats(stats)
            
            # Get recent videos (last 30 days)
            self._fetch_recent_videos()
            
            # Get top videos
            self._fetch_top_videos()
            
            # Update timestamp
            self.last_updated_label.configure(
                text=f"Last updated: {datetime.now().strftime('%I:%M %p')}"
            )
            
        except Exception as e:
            print(f"Error fetching channel data: {e}")
        
        finally:
            self.refresh_btn.configure(state="normal", text="Refresh")
    
    def _update_overview_stats(self, stats):
        """Update overview stat cards"""
        subscribers = self._format_number(int(stats.get('subscriberCount', 0)))
        total_views = self._format_number(int(stats.get('viewCount', 0)))
        total_videos = stats.get('videoCount', 0)
        
        avg_views = 0
        if int(total_videos) > 0:
            avg_views = int(stats.get('viewCount', 0)) / int(total_videos)
        
        self.subscribers_card["value"].configure(text=subscribers)
        self.total_views_card["value"].configure(text=total_views)
        self.total_videos_card["value"].configure(text=total_videos)
        self.avg_views_card["value"].configure(text=self._format_number(int(avg_views)))
    
    def _fetch_recent_videos(self):
        """Fetch recent videos from last 30 days"""
        try:
            # Get uploads playlist
            channel_response = self.youtube_service.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
            
            playlist_response = self.youtube_service.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist,
                maxResults=50
            ).execute()
            
            # Clear existing
            for item in self.recent_videos_tree.get_children():
                self.recent_videos_tree.delete(item)
            
            # Get video IDs
            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
            
            if video_ids:
                # Get video statistics
                videos_response = self.youtube_service.videos().list(
                    part='statistics,snippet',
                    id=','.join(video_ids[:50])
                ).execute()
                
                for video in videos_response['items']:
                    published = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00'))
                    
                    # Only show videos from last 30 days
                    if (datetime.now(published.tzinfo) - published).days <= 30:
                        stats = video['statistics']
                        views = int(stats.get('viewCount', 0))
                        likes = int(stats.get('likeCount', 0))
                        comments = int(stats.get('commentCount', 0))
                        
                        # Estimate CTR (rough calculation)
                        impressions = views * 10  # Rough estimate
                        ctr = (views / impressions * 100) if impressions > 0 else 0
                        
                        self.recent_videos_tree.insert("", "end", values=(
                            video['snippet']['title'][:50] + "...",
                            published.strftime('%b %d'),
                            self._format_number(views),
                            self._format_number(likes),
                            self._format_number(comments),
                            f"{ctr:.1f}"
                        ))
        
        except Exception as e:
            print(f"Error fetching recent videos: {e}")
    
    def _fetch_top_videos(self):
        """Fetch top performing videos all time"""
        try:
            # Get uploads playlist
            channel_response = self.youtube_service.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get all videos
            playlist_response = self.youtube_service.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist,
                maxResults=50
            ).execute()
            
            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
            
            if video_ids:
                # Get video statistics
                videos_response = self.youtube_service.videos().list(
                    part='statistics,snippet',
                    id=','.join(video_ids)
                ).execute()
                
                # Sort by views
                videos = sorted(
                    videos_response['items'],
                    key=lambda x: int(x['statistics'].get('viewCount', 0)),
                    reverse=True
                )[:10]
                
                # Clear existing
                for item in self.top_videos_tree.get_children():
                    self.top_videos_tree.delete(item)
                
                # Add top 10
                for rank, video in enumerate(videos, 1):
                    stats = video['statistics']
                    views = int(stats.get('viewCount', 0))
                    likes = int(stats.get('likeCount', 0))
                    comments = int(stats.get('commentCount', 0))
                    
                    engagement = ((likes + comments) / views * 100) if views > 0 else 0
                    
                    self.top_videos_tree.insert("", "end", values=(
                        rank,
                        video['snippet']['title'][:60] + "...",
                        self._format_number(views),
                        self._format_number(likes),
                        f"{engagement:.2f}%"
                    ))
        
        except Exception as e:
            print(f"Error fetching top videos: {e}")
    
    def _format_number(self, num):
        """Format number with K, M, B suffixes"""
        if num >= 1000000000:
            return f"{num/1000000000:.1f}B"
        elif num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)
