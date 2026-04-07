"""
RealE Tube - Theme Configuration
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

class ThemeConfig:
    """Theme configurations for RealE Tube"""
    
    MATRIX_HACKER = {
        "name": "Matrix Hacker",
        "bg_primary": "#000000",
        "bg_secondary": "#0a0a0a",
        "bg_tertiary": "#1a1a1a",
        "text_primary": "#00FF41",
        "text_secondary": "#39FF14",
        "text_tertiary": "#00CC33",
        "accent": "#00FF41",
        "accent_hover": "#39FF14",
        "border": "#00FF41",
        "button_bg": "#0a0a0a",
        "button_hover": "#1a1a1a",
        "input_bg": "#0a0a0a",
        "input_border": "#00FF41",
        "success": "#00FF41",
        "warning": "#FFD700",
        "error": "#FF0000",
        "font_family": "Courier New",
        "font_size_title": 28,
        "font_size_heading": 18,
        "font_size_body": 12,
        "font_size_small": 10,
        "glow_effect": True,
        "animation": "matrix_rain"
    }
    
    MODERN_PRO = {
        "name": "Modern Pro",
        "bg_primary": "#FFFFFF",
        "bg_secondary": "#F5F5F5",
        "bg_tertiary": "#E8E8E8",
        "text_primary": "#1976D2",
        "text_secondary": "#424242",
        "text_tertiary": "#757575",
        "accent": "#FF9800",
        "accent_hover": "#FFB74D",
        "border": "#E0E0E0",
        "button_bg": "#2196F3",
        "button_hover": "#64B5F6",
        "input_bg": "#FFFFFF",
        "input_border": "#BDBDBD",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "font_family": "SF Pro Display",
        "font_size_title": 32,
        "font_size_heading": 20,
        "font_size_body": 13,
        "font_size_small": 11,
        "glow_effect": False,
        "animation": None,
        "shadow": "0 4px 6px rgba(0,0,0,0.1)"
    }
    
    NEON_DARK = {
        "name": "Neon Dark",
        "bg_primary": "#0D0D0D",
        "bg_secondary": "#1A1A1A",
        "bg_tertiary": "#262626",
        "text_primary": "#FFFFFF",
        "text_secondary": "#E0E0E0",
        "text_tertiary": "#B0B0B0",
        "accent": "#FF6B35",
        "accent_hover": "#FF8555",
        "border": "#FF6B35",
        "button_bg": "#1A1A1A",
        "button_hover": "#262626",
        "input_bg": "#1A1A1A",
        "input_border": "#FF6B35",
        "success": "#00E676",
        "warning": "#FFD600",
        "error": "#FF1744",
        "font_family": "SF Pro Rounded",
        "font_size_title": 30,
        "font_size_heading": 19,
        "font_size_body": 13,
        "font_size_small": 11,
        "glow_effect": True,
        "animation": None,
        "neon_glow": "0 0 10px #FF6B35, 0 0 20px #FF6B35"
    }
    
    @staticmethod
    def get_theme(theme_name):
        """Get theme configuration by name"""
        themes = {
            "Matrix Hacker": ThemeConfig.MATRIX_HACKER,
            "Modern Pro": ThemeConfig.MODERN_PRO,
            "Neon Dark": ThemeConfig.NEON_DARK
        }
        return themes.get(theme_name, ThemeConfig.MODERN_PRO)
    
    @staticmethod
    def get_all_themes():
        """Get list of all available themes"""
        return ["Matrix Hacker", "Modern Pro", "Neon Dark"]
