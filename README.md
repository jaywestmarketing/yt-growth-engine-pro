# YT-Growth-Engine-Pro: The All-in-One YouTube SEO & Automation Framework

YT-Growth-Engine-Pro is a high-performance automation toolkit designed to hijack the YouTube algorithm. By combining deep metadata scraping with strategic engagement automation, this tool helps creators and marketers outrank competitors and secure top spots in Google Video Search.

## Core Capabilities

**Precision Metadata Scraping**: Instantly extract high-ranking titles, descriptions, and hidden tags from top-performing competitor videos to mirror their SEO success.

**Smart Content Matcher**: Uses NLP to analyze niche trends and identify "Content Gaps," ensuring your uploads are perfectly positioned for the "Suggested Video" sidebar.

**Triple-Mode Engagement Bot**:

- **Precision Mode**: Drops direct CTAs on high-traffic competing videos.
- **AI Context Mode**: Generates human-like, relevant comments based on video transcripts to bypass spam filters.
- **Community Mode**: Interacts with top comments on viral videos to funnel high-intent viewers to your link.

**Search Dominance**: Auto-optimizes video metadata for Google Search and YouTube's internal ranking signals.

## How to Trend & Scale

1. **Analyze**: Run the scraper to identify what the top 1% in your niche are doing.
2. **Optimize**: Apply the "Content Match" logic to your video uploads.
3. **Engage**: Deploy the multi-mode commenter to create a backlink loop from viral competitor videos.

## Features

**Automated Upload Pipeline**
- Monitor Google Drive for new videos
- AI-powered keyword generation
- Competitor analysis and tag hijacking
- Optimized title and description generation
- Automatic upload to YouTube

**Intelligent Retry System**
- Performance monitoring (views, CTR, engagement)
- Automatic deletion and retry for underperforming videos
- Up to 3 retry attempts with different keyword strategies
- Fully autonomous optimization

**Analytics Dashboard**
- Real-time upload tracking
- Performance metrics visualization
- Success rate analytics
- Best performing keyword analysis

**Three Custom Themes**
- **Matrix Hacker**: Neon green on black with hacker aesthetic
- **Modern Pro**: Blue and orange professional design
- **Neon Dark**: Dark theme with orange neon accents

**Fully Configurable**
- Adjustable performance thresholds
- Customizable retry intervals
- Keyword strategy controls
- API integration settings

## Installation

### Prerequisites

- macOS 11 or later
- Python 3.9+
- Google Cloud account with Drive & YouTube APIs enabled
- Anthropic Claude API key or Google Gemini API key

### Step 1: Clone or Download

```bash
git clone <repository-url>
cd reale-tube
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Add Your Logo

Place your logo as `assets/logo.png` (recommended: 64x64 or 128x128 pixels, PNG format)

### Step 4: Configure API Keys

1. Launch the application: `python main.py`
2. Go to the **Settings** tab
3. Upload your Google Drive API credentials (JSON file)
4. Upload your YouTube API credentials (JSON file)
5. Enter your Claude or Gemini API key
6. Enter your Google Drive folder ID and YouTube channel ID
7. Click **Save All Settings**

### Step 5: Build Standalone App (Optional)

To create a double-click executable:

```bash
python build_app.py
```

The app will be created in the `dist/` folder. Drag it to your Applications folder.

## Usage

### Running the Application

**Development mode:**
```bash
python main.py
```

**Standalone app:**
Double-click `RealE Tube.app` in your Applications folder

### Workflow

1. **Upload videos to Google Drive**
   - Drop your video file in the watched folder
   - Add a `description.txt` file with a brief description (e.g., "Tutorial on changing car oil")

2. **Automation runs automatically**
   - AI generates keywords from your description
   - Researches competitor videos (150+ likes)
   - Creates optimized title, description, and tags
   - Uploads to YouTube immediately

3. **Performance monitoring**
   - After 24 hours, checks: views >= 150, CTR >= 3%, engagement >= 6%
   - If underperforming, deletes and retries with new keywords
   - Up to 3 attempts before marking as abandoned

4. **Track results**
   - View all videos in the **Videos** tab
   - Monitor analytics in the **Analytics** tab
   - Check activity log in the **Dashboard**

## Configuration

### Performance Thresholds

Adjust in **Settings** > **Performance Thresholds**:
- **Minimum Views**: 50-500 (default: 150)
- **Minimum CTR**: 1-10% (default: 3%)
- **Minimum Engagement**: 1-15% (default: 6%)

### Retry Configuration

Adjust in **Settings** > **Retry Configuration**:
- **First Check Delay**: 12/24/48 hours (default: 24)
- **Second Check Delay**: 24/48/72 hours (default: 48)
- **Max Attempts**: 1-5 (default: 3)
- **Delete on Fail**: Toggle (default: ON)

### Keyword Strategy

Adjust in **Settings** > **Keyword Strategy**:
- **Competitor Min Likes**: 50-1000 (default: 150)
- **Competitors to Analyze**: 5-50 (default: 20)
- **Aggressiveness**: Low/Medium/High (default: Medium)

## System Tray

RealE Tube minimizes to the system tray. Access it by:
- Clicking the tray icon to show/hide window
- Right-click for menu options (Show/Quit)

## Themes

Switch themes in the **Themes** tab:

**Matrix Hacker**
- Neon green (#00FF41) on black (#000000)
- Courier New font
- Hacker aesthetic

**Modern Pro**
- Blue (#2196F3) and orange (#FF9800)
- SF Pro Display font
- Professional design with shadows

**Neon Dark**
- Orange neon (#FF6B35) on dark (#0D0D0D)
- SF Pro Rounded font
- Glowing neon effects

## Troubleshooting

**App won't launch:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

**API errors:**
- Verify API credentials are correct in Settings
- Ensure Google Cloud APIs are enabled (Drive, YouTube Data API v3)
- Check API quota limits in Google Cloud Console

**Videos not uploading:**
- Confirm Google Drive folder ID is correct
- Ensure YouTube channel ID is correct
- Check activity log for error messages

**Performance monitoring not working:**
- Verify API keys are valid
- Check that videos are public or unlisted (not private)
- Ensure sufficient time has passed for metrics

## Ethical Use & Disclaimer

This project is for educational and research purposes only. Users are responsible for adhering to YouTube's Terms of Service. Always use automation responsibly to build genuine community value.

## Support

For issues, feature requests, or questions:
- Create an issue in the repository
- Contact: RealE Technology Solutions

## License

Copyright © 2024 RealE Technology Solutions. All rights reserved.

Proprietary software - unauthorized copying, modification, or distribution is prohibited.

---

**Built with:**
- CustomTkinter for modern GUI
- Google APIs for Drive & YouTube integration
- Anthropic Claude / Google Gemini for AI-powered optimization

If this tool helps you scale your channel, please give it a star! It helps the project grow and stay updated.
