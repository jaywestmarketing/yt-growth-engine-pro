"""
RealE Tube - Main Application Window
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
from tkinter import PhotoImage
import os
from pathlib import Path
from gui.themes import ThemeConfig
from gui.dashboard import DashboardTab
from gui.settings import SettingsTab
from gui.videos import VideosTab
from gui.analytics import AnalyticsTab
from gui.theme_selector import ThemeSelectorTab

# Try to import pystray (requires Python 3.9+)
try:
    import pystray
    from PIL import Image
    import threading
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("Note: System tray feature disabled (requires Python 3.9+)")

class RealETubeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Application state
        self.current_theme = "Modern Pro"
        self.automation_running = False
        self.automation_engine = None
        
        # Window configuration
        self.setup_window()
        
        # Load logo
        self.logo = self.load_logo()
        
        # Apply initial theme
        self.apply_theme(self.current_theme)
        
        # Create UI
        self.create_header()
        self.create_tabs()
        
        # System tray (only if available)
        if TRAY_AVAILABLE:
            self.setup_system_tray()
        
        # Protocol for window close
        if TRAY_AVAILABLE:
            self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        else:
            self.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # Auto-start automation
        self.initialize_automation()
    
    def initialize_automation(self):
        """Initialize and start automation engine"""
        try:
            from automation.automation_engine import AutomationEngine
            from pathlib import Path
            import json
            
            # Load config
            config_path = Path(__file__).parent.parent / "config" / "config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Create automation engine with log callback
                self.automation_engine = AutomationEngine(
                    config,
                    log_callback=self.log_to_dashboard
                )
                
                # Start automation
                self.automation_engine.start()
                self.start_automation()
            else:
                self.log_to_dashboard("Config file not found - please configure settings first", "WARNING")
        
        except Exception as e:
            self.log_to_dashboard(f"Failed to initialize automation: {e}", "ERROR")
            print(f"Automation initialization error: {e}")
    
    def log_to_dashboard(self, message: str, log_type: str = "INFO"):
        """Log message to dashboard"""
        if hasattr(self, 'dashboard_tab'):
            self.dashboard_tab.add_log_entry(message, log_type)
    
    def setup_window(self):
        """Configure main window with 75% screen size"""
        self.title("RealE Tube - YouTube Automation Platform")
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate 75% size
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.75)
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(1000, 700)
    
    def load_logo(self):
        """Load logo from assets folder"""
        logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            try:
                return PhotoImage(file=str(logo_path))
            except Exception as e:
                print(f"Failed to load logo: {e}")
                return None
        return None
    
    def apply_theme(self, theme_name):
        """Apply selected theme to application"""
        self.current_theme = theme_name
        theme = ThemeConfig.get_theme(theme_name)
        
        # Set CustomTkinter theme mode
        if theme["bg_primary"] in ["#000000", "#0D0D0D"]:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        
        # Store theme config for access by child widgets
        self.theme_config = theme
        
        # Update background
        self.configure(fg_color=theme["bg_primary"])
    
    def create_header(self):
        """Create application header with logo and title"""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=self.theme_config["bg_secondary"],
            corner_radius=0,
            height=80
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo and title container
        title_container = ctk.CTkFrame(
            header_frame,
            fg_color="transparent"
        )
        title_container.pack(side="left", padx=30, pady=15)
        
        # Logo (if available)
        if self.logo:
            logo_label = ctk.CTkLabel(
                title_container,
                image=self.logo,
                text=""
            )
            logo_label.pack(side="left", padx=(0, 15))
        
        # App title
        title_label = ctk.CTkLabel(
            title_container,
            text="RealE Tube",
            font=(self.theme_config["font_family"], self.theme_config["font_size_title"], "bold"),
            text_color=self.theme_config["text_primary"]
        )
        title_label.pack(side="left")
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(
            header_frame,
            fg_color="transparent"
        )
        self.status_frame.pack(side="right", padx=30, pady=15)
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="● Automation Active",
            font=(self.theme_config["font_family"], self.theme_config["font_size_body"]),
            text_color=self.theme_config["success"]
        )
        self.status_indicator.pack()
    
    def create_tabs(self):
        """Create tabbed interface"""
        # Tab container
        tab_container = ctk.CTkFrame(
            self,
            fg_color=self.theme_config["bg_primary"]
        )
        tab_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(
            tab_container,
            fg_color=self.theme_config["bg_secondary"],
            segmented_button_fg_color=self.theme_config["bg_tertiary"],
            segmented_button_selected_color=self.theme_config["accent"],
            segmented_button_selected_hover_color=self.theme_config["accent_hover"],
            text_color=self.theme_config["text_primary"]
        )
        self.tabview.pack(fill="both", expand=True)
        
        # Add tabs
        self.tabview.add("Dashboard")
        self.tabview.add("Settings")
        self.tabview.add("Videos")
        self.tabview.add("Analytics")
        self.tabview.add("Themes")
        
        # Initialize tab content
        self.dashboard_tab = DashboardTab(
            self.tabview.tab("Dashboard"),
            self.theme_config,
            self
        )
        
        self.settings_tab = SettingsTab(
            self.tabview.tab("Settings"),
            self.theme_config,
            self
        )
        
        self.videos_tab = VideosTab(
            self.tabview.tab("Videos"),
            self.theme_config,
            self
        )
        
        self.analytics_tab = AnalyticsTab(
            self.tabview.tab("Analytics"),
            self.theme_config,
            self
        )
        
        self.theme_selector_tab = ThemeSelectorTab(
            self.tabview.tab("Themes"),
            self.theme_config,
            self
        )
    
    def setup_system_tray(self):
        """Setup system tray icon and menu (only on Python 3.9+)"""
        if not TRAY_AVAILABLE:
            return
            
        # Create a simple icon (will be replaced with actual icon)
        icon_image = Image.new('RGB', (64, 64), color='#FF6B35')
        
        menu = pystray.Menu(
            pystray.MenuItem('Show', self.show_window),
            pystray.MenuItem('Quit', self.quit_app)
        )
        
        self.tray_icon = pystray.Icon(
            "RealE Tube",
            icon_image,
            "RealE Tube - YouTube Automation",
            menu
        )
    
    def minimize_to_tray(self):
        """Minimize application to system tray (only on Python 3.9+)"""
        if not TRAY_AVAILABLE:
            self.quit_app()
            return
            
        self.withdraw()
        
        # Run tray icon in separate thread
        if not hasattr(self, 'tray_thread') or not self.tray_thread.is_alive():
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
    
    def show_window(self, icon=None, item=None):
        """Show application window from tray"""
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def quit_app(self, icon=None, item=None):
        """Quit application completely"""
        if TRAY_AVAILABLE and hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.destroy()
    
    def start_automation(self):
        """Start automation on app launch"""
        self.automation_running = True
        self.status_indicator.configure(
            text="● Automation Active",
            text_color=self.theme_config["success"]
        )
        # Start engine if available
        if self.automation_engine and not self.automation_engine.running:
            self.automation_engine.start()
    
    def stop_automation(self):
        """Stop automation"""
        self.automation_running = False
        self.status_indicator.configure(
            text="○ Automation Stopped",
            text_color=self.theme_config["error"]
        )
        # Stop engine if running
        if self.automation_engine and self.automation_engine.running:
            self.automation_engine.stop()
    
    def toggle_automation(self):
        """Toggle automation on/off"""
        if self.automation_running:
            self.stop_automation()
        else:
            self.start_automation()
    
    def switch_theme(self, theme_name):
        """Switch to a different theme without losing data"""
        old_automation_state = self.automation_running
        
        # Apply new theme
        self.apply_theme(theme_name)
        
        # Update existing widgets instead of recreating everything
        self._update_theme_colors()
        
        # Restore automation state
        self.automation_running = old_automation_state
    
    def _update_theme_colors(self):
        """Update colors of existing widgets without destroying them"""
        # Update main window background
        self.configure(fg_color=self.theme_config["bg_primary"])
        
        # Update header if it exists
        if hasattr(self, 'status_indicator'):
            if self.automation_running:
                self.status_indicator.configure(text_color=self.theme_config["success"])
            else:
                self.status_indicator.configure(text_color=self.theme_config["error"])
        
        # Force refresh of tabs with new theme
        if hasattr(self, 'tabview'):
            self.tabview.configure(
                fg_color=self.theme_config["bg_secondary"],
                segmented_button_fg_color=self.theme_config["bg_tertiary"],
                segmented_button_selected_color=self.theme_config["accent"],
                segmented_button_selected_hover_color=self.theme_config["accent_hover"],
                text_color=self.theme_config["text_primary"]
            )
        
        # Let tabs know theme changed so they can update their colors
        if hasattr(self, 'dashboard_tab'):
            self.dashboard_tab.theme = self.theme_config
        if hasattr(self, 'settings_tab'):
            self.settings_tab.theme = self.theme_config
        if hasattr(self, 'videos_tab'):
            self.videos_tab.theme = self.theme_config
        if hasattr(self, 'analytics_tab'):
            self.analytics_tab.theme = self.theme_config
        if hasattr(self, 'theme_selector_tab'):
            self.theme_selector_tab.theme = self.theme_config

if __name__ == "__main__":
    app = RealETubeApp()
    app.mainloop()
