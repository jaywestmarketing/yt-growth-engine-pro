# -*- coding: utf-8 -*-
"""
RealE Tube - Settings Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import filedialog
import json
from pathlib import Path

class SettingsTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        
        # Default settings
        self.settings = self.load_settings()
        
        self.create_settings()
    
    def load_settings(self):
        """Load settings from config file, merging with defaults for new keys"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        defaults = self._get_defaults()

        if config_path.exists():
            with open(config_path, 'r') as f:
                saved = json.load(f)
            # Merge: saved values win, but missing keys get defaults
            for section, section_defaults in defaults.items():
                if section not in saved:
                    saved[section] = section_defaults
                elif isinstance(section_defaults, dict):
                    for key, val in section_defaults.items():
                        if key not in saved[section]:
                            saved[section][key] = val
            return saved

        return defaults

    def _get_defaults(self):
        """Return default settings dictionary"""
        return {
            "api": {
                "google_drive_credentials": "",
                "youtube_credentials": "",
                "ai_api_key": ""
            },
            "monitoring": {
                "drive_folder_id": "",
                "youtube_channel_id": ""
            },
            "performance": {
                "min_views": 150,
                "min_ctr": 3.0,
                "min_engagement": 6.0,
                "engagement_required": False,
                "view_protection_multiplier": 2.0
            },
            "retry": {
                "first_check_hours": 24,
                "second_check_hours": 48,
                "max_attempts": 3,
                "delete_on_fail": True
            },
            "keywords": {
                "competitor_min_likes": 150,
                "competitors_to_analyze": 20,
                "competitor_max_age_days": 0,
                "keyword_aggressiveness": "Medium"
            },
            "comment_bot": {
                "enabled": True,
                "comment_style": "helpful",
                "max_comments_per_video": 3,
                "delay_seconds": 30
            },
            "theme": {
                "current": "Modern Pro"
            }
        }
    
    def save_settings(self):
        """Save settings to config file"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)
        
        # Show success message
        self.app.dashboard_tab.add_log_entry("Settings saved successfully", "SUCCESS")
    
    def create_settings(self):
        """Create settings layout"""
        # Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # API Configuration Section
        self.create_section(scroll_frame, "API Configuration", [
            self.create_api_settings
        ])
        
        # Monitoring Settings Section
        self.create_section(scroll_frame, "Monitoring Settings", [
            self.create_monitoring_settings
        ])
        
        # Performance Thresholds Section
        self.create_section(scroll_frame, "Performance Thresholds", [
            self.create_performance_settings
        ])
        
        # Retry Configuration Section
        self.create_section(scroll_frame, "Retry Configuration", [
            self.create_retry_settings
        ])
        
        # Keyword Strategy Section
        self.create_section(scroll_frame, "Keyword Strategy", [
            self.create_keyword_settings
        ])
        
        # Comment Bot Section
        self.create_section(scroll_frame, "Comment Bot", [
            self.create_comment_bot_settings
        ])
        
        # Save button
        save_button = ctk.CTkButton(
            scroll_frame,
            text="Save All Settings",
            font=(self.theme["font_family"], self.theme["font_size_body"], "bold"),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            height=50,
            corner_radius=8,
            command=self.save_settings
        )
        save_button.pack(fill="x", pady=(30, 0))
    
    def create_section(self, parent, title, creators):
        """Create a settings section"""
        section_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=(self.theme["font_family"], self.theme["font_size_heading"], "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title_label.pack(fill="x", padx=20, pady=(20, 15))
        
        # Content
        for creator in creators:
            creator(section_frame)
    
    def create_api_settings(self, parent):
        """Create API configuration fields"""
        # Google Drive Credentials
        self.create_file_input(
            parent,
            "Google Drive API Credentials",
            "google_drive_credentials",
            "api"
        )
        
        # YouTube Credentials
        self.create_file_input(
            parent,
            "YouTube API Credentials",
            "youtube_credentials",
            "api"
        )
        
        # AI API Key with verification
        self.create_text_input_with_verify(
            parent,
            "Claude API Key",
            "ai_api_key",
            "api",
            show="*"
        )
    
    def create_monitoring_settings(self, parent):
        """Create monitoring configuration fields"""
        self.create_text_input(
            parent,
            "Google Drive Folder ID",
            "drive_folder_id",
            "monitoring"
        )
        
        self.create_text_input(
            parent,
            "YouTube Channel ID",
            "youtube_channel_id",
            "monitoring"
        )
    
    def create_performance_settings(self, parent):
        """Create performance threshold settings"""
        self.create_slider_input(
            parent,
            "Minimum Views",
            "min_views",
            "performance",
            50, 500, 150
        )
        
        self.create_slider_input(
            parent,
            "Minimum CTR (%)",
            "min_ctr",
            "performance",
            1.0, 10.0, 3.0,
            step=0.1
        )
        
        self.create_slider_input(
            parent,
            "Minimum Engagement Rate (%)",
            "min_engagement",
            "performance",
            1.0, 15.0, 6.0,
            step=0.1
        )

        self.create_toggle_input(
            parent,
            "Require Engagement (OFF = views-only mode, never delete for low engagement)",
            "engagement_required",
            "performance"
        )

        self.create_slider_input(
            parent,
            "View Protection Multiplier (videos with views above min_views x this are NEVER deleted)",
            "view_protection_multiplier",
            "performance",
            1.0, 10.0, 2.0,
            step=0.5
        )
    
    def create_retry_settings(self, parent):
        """Create retry configuration settings"""
        self.create_option_input(
            parent,
            "First Check Delay (hours)",
            "first_check_hours",
            "retry",
            [12, 24, 48]
        )
        
        self.create_option_input(
            parent,
            "Second Check Delay (hours)",
            "second_check_hours",
            "retry",
            [24, 48, 72]
        )
        
        self.create_slider_input(
            parent,
            "Max Retry Attempts",
            "max_attempts",
            "retry",
            1, 5, 3
        )
        
        self.create_toggle_input(
            parent,
            "Delete Immediately on Fail",
            "delete_on_fail",
            "retry"
        )
    
    def create_keyword_settings(self, parent):
        """Create keyword strategy settings"""
        self.create_slider_input(
            parent,
            "Competitor Minimum Likes",
            "competitor_min_likes",
            "keywords",
            50, 1000, 150
        )
        
        self.create_slider_input(
            parent,
            "Number of Competitors to Analyze",
            "competitors_to_analyze",
            "keywords",
            5, 50, 20
        )

        # Max age of competitor videos in days. 0 means "no limit" —
        # use anything that matches our keywords, regardless of when
        # it was uploaded.
        self.create_slider_input(
            parent,
            "Competitor Max Age (days, 0 = no limit)",
            "competitor_max_age_days",
            "keywords",
            0, 730, 0
        )

        self.create_option_input(
            parent,
            "Keyword Variation Aggressiveness",
            "keyword_aggressiveness",
            "keywords",
            ["Low", "Medium", "High"]
        )
    
    def create_comment_bot_settings(self, parent):
        """Create comment bot settings"""
        self.create_toggle_input(
            parent,
            "Enable Comment Bot (posts on competitor videos)",
            "enabled",
            "comment_bot"
        )
        
        self.create_option_input(
            parent,
            "Comment Style",
            "comment_style",
            "comment_bot",
            ["helpful", "question", "appreciation", "engaging"]
        )
        
        self.create_slider_input(
            parent,
            "Max Comments Per Upload",
            "max_comments_per_video",
            "comment_bot",
            0, 10, 3
        )
        
        self.create_slider_input(
            parent,
            "Delay Between Comments (seconds)",
            "delay_seconds",
            "comment_bot",
            10, 120, 30
        )
    
    def create_text_input(self, parent, label, key, section, show=None):
        """Create text input field"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 15))
        
        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            container,
            fg_color=self.theme["input_bg"],
            border_color=self.theme["input_border"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            height=40,
            show=show
        )
        entry.insert(0, self.settings[section][key])
        entry.pack(fill="x")
        
        # Bind to update settings
        entry.bind("<KeyRelease>", lambda e: self.update_setting(section, key, entry.get()))
    
    def create_text_input_with_verify(self, parent, label, key, section, show=None):
        """Create text input field with verify button"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 15))
        
        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(0, 5))
        
        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.pack(fill="x")
        
        entry = ctk.CTkEntry(
            input_frame,
            fg_color=self.theme["input_bg"],
            border_color=self.theme["input_border"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            height=40,
            show=show
        )
        entry.insert(0, self.settings[section][key])
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Verify button
        verify_btn = ctk.CTkButton(
            input_frame,
            text="Verify",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="#FFFFFF",
            width=80,
            height=40,
            command=lambda: self.verify_api_key(entry, key, section)
        )
        verify_btn.pack(side="right")
        
        # Bind to update settings
        entry.bind("<KeyRelease>", lambda e: self.update_setting(section, key, entry.get()))
    
    def create_file_input(self, parent, label, key, section):
        """Create file input field with browse button"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 15))
        
        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(0, 5))
        
        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.pack(fill="x")
        
        entry = ctk.CTkEntry(
            input_frame,
            fg_color=self.theme["input_bg"],
            border_color=self.theme["input_border"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            height=40
        )
        entry.insert(0, self.settings[section][key])
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            input_frame,
            text="Browse",
            font=(self.theme["font_family"], self.theme["font_size_small"]),
            fg_color=self.theme["button_bg"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text_primary"],
            width=80,
            height=40,
            command=lambda: self.browse_file(entry, section, key)
        )
        browse_btn.pack(side="right")
    
    def create_slider_input(self, parent, label, key, section, min_val, max_val, default, step=1):
        """Create slider input field"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 15))
        
        label_widget = ctk.CTkLabel(
            container,
            text=f"{label}: {self.settings[section][key]}",
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(0, 5))
        
        slider = ctk.CTkSlider(
            container,
            from_=min_val,
            to=max_val,
            number_of_steps=int((max_val - min_val) / step),
            fg_color=self.theme["bg_tertiary"],
            progress_color=self.theme["accent"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            height=20,
            command=lambda v: self.update_slider(label_widget, label, section, key, v, step)
        )
        slider.set(self.settings[section][key])
        slider.pack(fill="x")
    
    def create_option_input(self, parent, label, key, section, options):
        """Create dropdown option input"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 15))
        
        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(0, 5))
        
        dropdown = ctk.CTkOptionMenu(
            container,
            values=[str(opt) for opt in options],
            fg_color=self.theme["button_bg"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            text_color=self.theme["text_primary"],
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            dropdown_font=(self.theme["font_family"], self.theme["font_size_body"]),
            height=40,
            command=lambda v: self.update_setting(section, key, int(v) if v.isdigit() else v)
        )
        dropdown.set(str(self.settings[section][key]))
        dropdown.pack(fill="x")
    
    def create_toggle_input(self, parent, label, key, section):
        """Create toggle switch input"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 15))
        
        switch = ctk.CTkSwitch(
            container,
            text=label,
            font=(self.theme["font_family"], self.theme["font_size_body"]),
            text_color=self.theme["text_secondary"],
            fg_color=self.theme["bg_tertiary"],
            progress_color=self.theme["accent"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            command=lambda: self.update_setting(section, key, switch.get())
        )
        if self.settings[section][key]:
            switch.select()
        switch.pack(fill="x")
    
    def browse_file(self, entry, section, key):
        """Open file browser"""
        filename = filedialog.askopenfilename(
            title=f"Select {key}",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            entry.delete(0, "end")
            entry.insert(0, filename)
            self.update_setting(section, key, filename)
    
    def update_setting(self, section, key, value):
        """Update setting value"""
        self.settings[section][key] = value
    
    def update_slider(self, label_widget, label_text, section, key, value, step):
        """Update slider value and label"""
        # Round to step precision
        rounded_value = round(float(value) / step) * step
        self.settings[section][key] = rounded_value
        label_widget.configure(text=f"{label_text}: {rounded_value}")
    
    def verify_api_key(self, entry, key, section):
        """Verify API key is valid"""
        api_key = entry.get().strip()
        
        if not api_key:
            self.app.dashboard_tab.add_log_entry("API key is empty", "ERROR")
            return
        
        # Test the API key
        try:
            from anthropic import Anthropic
            
            self.app.dashboard_tab.add_log_entry("Verifying Claude API key...", "INFO")
            
            client = Anthropic(api_key=api_key)
            
            # Simple test request
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            
            # If we get here, the key is valid
            self.app.dashboard_tab.add_log_entry("✓ Claude API key verified successfully!", "SUCCESS")
            self.update_setting(section, key, api_key)
            
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                self.app.dashboard_tab.add_log_entry("✗ Invalid API key - authentication failed", "ERROR")
            else:
                self.app.dashboard_tab.add_log_entry(f"✗ Verification failed: {error_msg}", "ERROR")
