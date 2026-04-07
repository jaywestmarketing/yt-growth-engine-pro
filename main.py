#!/usr/bin/env python3
"""
RealE Tube - YouTube Automation Platform
Copyright © 2024 RealE Technology Solutions. All rights reserved.

Main application entry point
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import RealETubeApp

def main():
    """Initialize and run RealE Tube application"""
    print("Starting RealE Tube...")
    print("Copyright © 2024 RealE Technology Solutions")
    print("-" * 50)
    
    app = RealETubeApp()
    app.mainloop()

if __name__ == "__main__":
    main()
