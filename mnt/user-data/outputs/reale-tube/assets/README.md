# RealE Tube Assets

## Logo Requirements

Place your RealE Tube logo in this directory as:

**Filename:** `logo.png`

**Recommended specifications:**
- Format: PNG with transparency
- Size: 64x64 pixels or 128x128 pixels
- Aspect ratio: 1:1 (square)
- File size: < 100KB

The logo will be displayed in the application header next to the "RealE Tube" title.

## App Icon (for macOS executable)

For the macOS app bundle icon:

**Filename:** `icon.icns`

You can convert your logo to .icns format using online tools or:
```bash
# On macOS with Xcode tools
iconutil -c icns logo.iconset
```

## System Tray Icon

The system tray icon will be automatically generated from the logo, but you can also provide a custom tray icon:

**Filename:** `tray_icon.png`
- Format: PNG
- Size: 32x32 pixels
- Simple design (visible at small sizes)
