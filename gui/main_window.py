# -*- coding: utf-8 -*-
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
from gui.channel_dashboard import ChannelDashboardTab
from gui.manual_comment import ManualCommentTab
from gui.theme_selector import ThemeSelectorTab
from gui.ab_testing import ABTestingTab
from gui.shorts_pipeline import ShortsPipelineTab
from gui.scheduling import SchedulingTab
from gui.seo_scorecard import SEOScorecardTab
from gui.competitor_tracking import CompetitorTrackingTab
from gui.trend_detection import TrendDetectionTab
from gui.content_planner import ContentPlannerTab
from gui.revenue_analytics import RevenueAnalyticsTab
from gui.retention_heatmap import RetentionHeatmapTab
from gui.cross_platform import CrossPlatformTab
from gui.notifications_tab import NotificationsTab
from gui.collaboration import CollaborationTab
from gui.predictive import PredictiveTab
from gui.lifecycle import LifecycleTab
from gui.multi_channel import MultiChannelTab

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
    
    def initialize_manual_comment_bot(self):
        """Initialize the manual comment bot with credentials"""
        try:
            from automation.standalone_comment_bot import StandaloneCommentBot
            from pathlib import Path
            import json
            
            # Load config
            config_path = Path(__file__).parent.parent / "config" / "config.json"
            if not config_path.exists():
                return
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check if credentials are available
            youtube_creds = config['api'].get('youtube_credentials')
            claude_key = config['api'].get('ai_api_key')
            
            if youtube_creds and Path(youtube_creds).exists() and claude_key:
                from automation.google_auth import GoogleAuthHelper
                from automation.keyword_generator import KeywordGenerator
                
                # Get authenticated services
                auth_helper = GoogleAuthHelper(youtube_creds)
                youtube_service = auth_helper.get_youtube_service()
                ai_generator = KeywordGenerator(claude_key)
                
                # Create standalone bot
                standalone_bot = StandaloneCommentBot(youtube_service, ai_generator)
                
                # Set it in the manual comment tab
                self.manual_comment_tab.set_bot(standalone_bot)
                
                # Also set YouTube service for channel dashboard
                channel_id = config['monitoring'].get('youtube_channel_id')
                if channel_id:
                    self.channel_dashboard_tab.set_youtube_service(youtube_service, channel_id)
                
                self.log_to_dashboard("Manual comment bot initialized", "SUCCESS")
            else:
                self.log_to_dashboard("Manual comment bot requires credentials in Settings", "WARNING")
                
        except Exception as e:
            self.log_to_dashboard(f"Error initializing manual comment bot: {e}", "ERROR")
            print(f"Manual comment bot error: {e}")
    
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
        
        # Add tabs — grouped logically
        # Core
        self.tabview.add("Dashboard")
        self.tabview.add("Videos")
        self.tabview.add("Analytics")
        self.tabview.add("Channel")
        # Upload & Content
        self.tabview.add("Schedule")
        self.tabview.add("Shorts")
        self.tabview.add("A/B Testing")
        self.tabview.add("Content Plan")
        # Research & Growth
        self.tabview.add("SEO Score")
        self.tabview.add("Competitors")
        self.tabview.add("Trends")
        self.tabview.add("Lifecycle")
        # Analytics Extended
        self.tabview.add("Revenue")
        self.tabview.add("Retention")
        self.tabview.add("Predictive")
        # Platform & Settings
        self.tabview.add("Multi-Channel")
        self.tabview.add("Cross-Platform")
        self.tabview.add("Notifications")
        self.tabview.add("Collaboration")
        self.tabview.add("Manual Comment")
        self.tabview.add("Settings")
        self.tabview.add("Themes")

        # ── Initialize tab content ────────────────────────────────
        # Core
        self.dashboard_tab = DashboardTab(
            self.tabview.tab("Dashboard"), self.theme_config, self)
        self.videos_tab = VideosTab(
            self.tabview.tab("Videos"), self.theme_config, self)
        self.analytics_tab = AnalyticsTab(
            self.tabview.tab("Analytics"), self.theme_config, self)
        self.channel_dashboard_tab = ChannelDashboardTab(
            self.tabview.tab("Channel"), self.theme_config)

        # Upload & Content
        self.scheduling_tab = SchedulingTab(
            self.tabview.tab("Schedule"), self.theme_config, self)
        self.shorts_tab = ShortsPipelineTab(
            self.tabview.tab("Shorts"), self.theme_config, self)
        self.ab_testing_tab = ABTestingTab(
            self.tabview.tab("A/B Testing"), self.theme_config, self)
        self.content_planner_tab = ContentPlannerTab(
            self.tabview.tab("Content Plan"), self.theme_config, self)

        # Research & Growth
        self.seo_scorecard_tab = SEOScorecardTab(
            self.tabview.tab("SEO Score"), self.theme_config, self)
        self.competitor_tracking_tab = CompetitorTrackingTab(
            self.tabview.tab("Competitors"), self.theme_config, self)
        self.trend_detection_tab = TrendDetectionTab(
            self.tabview.tab("Trends"), self.theme_config, self)
        self.lifecycle_tab = LifecycleTab(
            self.tabview.tab("Lifecycle"), self.theme_config, self)

        # Analytics Extended
        self.revenue_tab = RevenueAnalyticsTab(
            self.tabview.tab("Revenue"), self.theme_config, self)
        self.retention_tab = RetentionHeatmapTab(
            self.tabview.tab("Retention"), self.theme_config, self)
        self.predictive_tab = PredictiveTab(
            self.tabview.tab("Predictive"), self.theme_config, self)

        # Platform & Settings
        self.multi_channel_tab = MultiChannelTab(
            self.tabview.tab("Multi-Channel"), self.theme_config, self)
        self.cross_platform_tab = CrossPlatformTab(
            self.tabview.tab("Cross-Platform"), self.theme_config, self)
        self.notifications_tab = NotificationsTab(
            self.tabview.tab("Notifications"), self.theme_config, self)
        self.collaboration_tab = CollaborationTab(
            self.tabview.tab("Collaboration"), self.theme_config, self)
        self.manual_comment_tab = ManualCommentTab(
            self.tabview.tab("Manual Comment"), self.theme_config)
        self.settings_tab = SettingsTab(
            self.tabview.tab("Settings"), self.theme_config, self)
        self.theme_selector_tab = ThemeSelectorTab(
            self.tabview.tab("Themes"), self.theme_config, self)
        
        # Initialize manual comment bot after automation engine is ready
        self.after(1000, self.initialize_manual_comment_bot)
    
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
        tab_attrs = [
            'dashboard_tab', 'settings_tab', 'videos_tab', 'analytics_tab',
            'channel_dashboard_tab', 'manual_comment_tab', 'theme_selector_tab',
            'scheduling_tab', 'shorts_tab', 'ab_testing_tab', 'content_planner_tab',
            'seo_scorecard_tab', 'competitor_tracking_tab', 'trend_detection_tab',
            'lifecycle_tab', 'revenue_tab', 'retention_tab', 'predictive_tab',
            'multi_channel_tab', 'cross_platform_tab', 'notifications_tab',
            'collaboration_tab',
        ]
        for attr in tab_attrs:
            if hasattr(self, attr):
                getattr(self, attr).theme = self.theme_config

if __name__ == "__main__":
    app = RealETubeApp()
    app.mainloop()
