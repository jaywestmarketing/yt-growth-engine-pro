# -*- coding: utf-8 -*-
"""
RealE Tube - Theme Selector Tab
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from gui.themes import ThemeConfig

class ThemeSelectorTab:
    def __init__(self, parent, theme_config, app):
        self.parent = parent
        self.theme = theme_config
        self.app = app
        
        self.create_theme_selector()
    
    def create_theme_selector(self):
        """Create theme selector layout"""
        # Main container
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="Choose Your Theme",
            font=(self.theme["font_family"], self.theme["font_size_title"], "bold"),
            text_color=self.theme["text_primary"]
        )
        header.pack(pady=(0, 30))
        
        # Theme grid
        themes_container = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        themes_container.pack(fill="both", expand=True)
        themes_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Create theme cards
        self.create_theme_card(
            themes_container,
            "Matrix Hacker",
            "Neon green on black with animated matrix rain background",
            ThemeConfig.MATRIX_HACKER,
            0
        )
        
        self.create_theme_card(
            themes_container,
            "Modern Pro",
            "Blue and orange with shadows and gradient accents",
            ThemeConfig.MODERN_PRO,
            1
        )
        
        self.create_theme_card(
            themes_container,
            "Neon Dark",
            "Dark background with orange neon glowing lines and modern styling",
            ThemeConfig.NEON_DARK,
            2
        )
    
    def create_theme_card(self, parent, name, description, theme_config, column):
        """Create individual theme preview card"""
        # Determine if this is the current theme
        is_current = (name == self.app.current_theme)
        
        # Card container
        if is_current:
            card = ctk.CTkFrame(
                parent,
                fg_color=theme_config["bg_secondary"],
                corner_radius=15,
                border_width=3,
                border_color=theme_config["accent"]
            )
        else:
            card = ctk.CTkFrame(
                parent,
                fg_color=theme_config["bg_secondary"],
                corner_radius=15,
                border_width=0
            )
        card.grid(row=0, column=column, padx=15, sticky="nsew")
        
        # Theme name
        name_label = ctk.CTkLabel(
            card,
            text=name,
            font=(theme_config["font_family"], theme_config["font_size_heading"], "bold"),
            text_color=theme_config["text_primary"]
        )
        name_label.pack(pady=(25, 10))
        
        # Preview area
        preview = ctk.CTkFrame(
            card,
            fg_color=theme_config["bg_primary"],
            corner_radius=10,
            height=200
        )
        preview.pack(fill="x", padx=20, pady=(0, 15))
        preview.pack_propagate(False)
        
        # Sample UI elements in preview
        self.create_preview_content(preview, theme_config)
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=(theme_config["font_family"], theme_config["font_size_small"]),
            text_color=theme_config["text_tertiary"],
            wraplength=250,
            justify="center"
        )
        desc_label.pack(pady=(0, 15), padx=20)
        
        # Color palette
        self.create_color_palette(card, theme_config)
        
        # Apply button
        button_text = "Current Theme" if is_current else "Apply Theme"
        apply_button = ctk.CTkButton(
            card,
            text=button_text,
            font=(theme_config["font_family"], theme_config["font_size_body"], "bold"),
            fg_color=theme_config["accent"] if not is_current else theme_config["bg_tertiary"],
            hover_color=theme_config["accent_hover"] if not is_current else theme_config["bg_tertiary"],
            text_color="#FFFFFF" if not is_current else theme_config["text_tertiary"],
            height=45,
            corner_radius=8,
            command=lambda: self.apply_theme(name) if not is_current else None,
            state="normal" if not is_current else "disabled"
        )
        apply_button.pack(fill="x", padx=20, pady=(15, 25))
    
    def create_preview_content(self, preview, theme_config):
        """Create sample UI elements in preview"""
        # Sample button
        sample_button = ctk.CTkButton(
            preview,
            text="Sample Button",
            font=(theme_config["font_family"], theme_config["font_size_small"]),
            fg_color=theme_config["button_bg"],
            hover_color=theme_config["button_hover"],
            text_color=theme_config["text_primary"],
            height=30,
            corner_radius=6
        )
        sample_button.pack(pady=(20, 10))
        
        # Sample text
        sample_text = ctk.CTkLabel(
            preview,
            text="Sample Text Content",
            font=(theme_config["font_family"], theme_config["font_size_body"]),
            text_color=theme_config["text_primary"]
        )
        sample_text.pack(pady=(0, 10))
        
        # Sample accent element
        accent_label = ctk.CTkLabel(
            preview,
            text="● Accent Color",
            font=(theme_config["font_family"], theme_config["font_size_small"]),
            text_color=theme_config["accent"]
        )
        accent_label.pack(pady=(0, 20))
    
    def create_color_palette(self, parent, theme_config):
        """Create color palette display"""
        palette_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        palette_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Color swatches
        colors = [
            ("Primary", theme_config["bg_primary"]),
            ("Accent", theme_config["accent"]),
            ("Text", theme_config["text_primary"]),
            ("Success", theme_config["success"]),
        ]
        
        for label, color in colors:
            swatch_container = ctk.CTkFrame(
                palette_frame,
                fg_color="transparent"
            )
            swatch_container.pack(side="left", expand=True)
            
            # Color circle
            swatch = ctk.CTkFrame(
                swatch_container,
                fg_color=color,
                width=30,
                height=30,
                corner_radius=15
            )
            swatch.pack()
            
            # Label
            label_widget = ctk.CTkLabel(
                swatch_container,
                text=label,
                font=(theme_config["font_family"], 8),
                text_color=theme_config["text_tertiary"]
            )
            label_widget.pack(pady=(3, 0))
    
    def apply_theme(self, theme_name):
        """Apply selected theme"""
        self.app.switch_theme(theme_name)
        self.app.dashboard_tab.add_log_entry(f"Theme changed to: {theme_name}", "SUCCESS")
