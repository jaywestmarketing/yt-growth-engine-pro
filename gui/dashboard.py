# -*- coding: utf-8 -*-
"""
RealE Tube - Dashboard Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from datetime import datetime

class DashboardTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        
        self.create_dashboard()
    
    def create_dashboard(self):
        """Create dashboard layout"""
        # Main container
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top stats section
        self.create_stats_section(main_frame)
        
        # Activity log section
        self.create_activity_log(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
    
    def create_stats_section(self, parent):
        """Create statistics cards"""
        stats_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Configure grid
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stat cards
        self.create_stat_card(
            stats_frame,
            "Active Uploads",
            "0",
            self.theme["accent"],
            0
        )
        
        self.create_stat_card(
            stats_frame,
            "Success Rate",
            "0%",
            self.theme["success"],
            1
        )
        
        self.create_stat_card(
            stats_frame,
            "In Retry",
            "0",
            self.theme["warning"],
            2
        )
        
        self.create_stat_card(
            stats_frame,
            "Abandoned",
            "0",
            self.theme["error"],
            3
        )
    
    def create_stat_card(self, parent, title, value, color, column):
        """Create individual stat card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10,
            border_width=2,
            border_color=color
        )
        card.grid(row=0, column=column, padx=10, sticky="ew")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            text_color=self.theme["text_tertiary"]
        )
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(self.theme["font_family"], self.theme["font_size_title"], "bold"),
            text_color=color
        )
        value_label.pack(pady=(0, 15))
    
    def create_activity_log(self, parent):
        """Create activity log section"""
        log_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        log_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Header
        header = ctk.CTkLabel(
            log_frame,
            text="Recent Activity",
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Scrollable log area
        self.log_text = ctk.CTkTextbox(
            log_frame,
            fg_color=self.theme["bg_tertiary"],
            text_color=self.theme["text_secondary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            wrap="word",
            height=300
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add initial log entry
        self.add_log_entry("System initialized - Automation ready", "SUCCESS")
    
    def create_control_buttons(self, parent):
        """Create automation control buttons"""
        control_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        control_frame.pack(fill="x")
        
        # Start/Stop button
        self.toggle_button = ctk.CTkButton(
            control_frame,
            text="Stop Automation",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["error"],
            hover_color=self.theme["error"],
            text_color="#FFFFFF",
            height=45,
            corner_radius=8,
            command=self.toggle_automation
        )
        self.toggle_button.pack(side="left", padx=(0, 10))
        
        # Clear log button
        clear_button = ctk.CTkButton(
            control_frame,
            text="Clear Log",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            fg_color=self.theme["bg_tertiary"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text_primary"],
            height=45,
            corner_radius=8,
            command=self.clear_log
        )
        clear_button.pack(side="left")
    
    def toggle_automation(self):
        """Toggle automation on/off"""
        self.app.toggle_automation()
        
        if self.app.automation_running:
            self.toggle_button.configure(
                text="Stop Automation",
                fg_color=self.theme["error"]
            )
            self.add_log_entry("Automation started", "SUCCESS")
        else:
            self.toggle_button.configure(
                text="Start Automation",
                fg_color=self.theme["success"]
            )
            self.add_log_entry("Automation stopped", "WARNING")
    
    def add_log_entry(self, message, log_type="INFO"):
        """Add entry to activity log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color based on log type
        color_map = {
            "SUCCESS": self.theme["success"],
            "WARNING": self.theme["warning"],
            "ERROR": self.theme["error"],
            "INFO": self.theme["text_secondary"]
        }
        color = color_map.get(log_type, self.theme["text_secondary"])
        
        # Insert log entry
        self.log_text.insert("end", f"[{timestamp}] ", "timestamp")
        self.log_text.insert("end", f"[{log_type}] ", f"type_{log_type}")
        self.log_text.insert("end", f"{message}\n")
        
        # Configure tags
        self.log_text.tag_config("timestamp", foreground=self.theme["text_tertiary"])
        self.log_text.tag_config(f"type_{log_type}", foreground=color)
        
        # Auto-scroll to bottom
        self.log_text.see("end")
    
    def clear_log(self):
        """Clear activity log"""
        self.log_text.delete("1.0", "end")
        self.add_log_entry("Log cleared", "INFO")
