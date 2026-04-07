"""
RealE Tube - Build Script for macOS Executable
Copyright © 2024 RealE Technology Solutions. All rights reserved.

Run this script to create a standalone macOS application:
    python build_app.py
"""

import PyInstaller.__main__
import os
from pathlib import Path

# Get project root
project_root = Path(__file__).parent

# PyInstaller configuration
PyInstaller.__main__.run([
    str(project_root / 'main.py'),
    '--name=RealE Tube',
    '--windowed',
    '--onefile',
    '--icon=' + str(project_root / 'assets' / 'icon.icns'),
    '--add-data=' + str(project_root / 'assets') + ':assets',
    '--add-data=' + str(project_root / 'config') + ':config',
    '--hidden-import=customtkinter',
    '--hidden-import=PIL',
    '--hidden-import=pystray',
    '--clean',
    '--noconfirm',
])

print("\n" + "="*60)
print("Build complete!")
print("="*60)
print(f"\nYour application is located in: {project_root / 'dist'}")
print("\nTo install:")
print("1. Navigate to the 'dist' folder")
print("2. Drag 'RealE Tube.app' to your Applications folder")
print("3. Double-click to launch!")
print("\nNote: On first launch, you may need to:")
print("- Right-click the app and select 'Open'")
print("- Allow the app in System Preferences > Security & Privacy")
