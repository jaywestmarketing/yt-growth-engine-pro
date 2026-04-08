# -*- coding: utf-8 -*-
"""
RealE Tube - Web Launcher
Runs the application as a local web interface when Tkinter is unavailable.
No external dependencies required - uses only Python standard library.

Usage: python3 web_app.py
Then open http://localhost:8080 in your browser.
"""

import http.server
import json
import urllib.parse
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import DatabaseManager

PORT = 8080
db = DatabaseManager()


def safe_str(val, default=""):
    return str(val) if val is not None else default


def safe_float(val, default=0.0):
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default


def safe_int(val, default=0):
    try:
        return int(val) if val is not None else default
    except (TypeError, ValueError):
        return default


def get_dashboard_html():
    """Generate the full single-page dashboard HTML."""
    # Load stats
    try:
        stats = db.get_statistics()
        by_status = stats.get('by_status', {})
        total = sum(by_status.values())
        success_rate = safe_float(stats.get('success_rate'))
        avg_attempts = safe_float(stats.get('avg_attempts'))
    except Exception:
        by_status, total, success_rate, avg_attempts = {}, 0, 0.0, 0.0

    # Load videos
    try:
        videos = db.get_all_videos()
    except Exception:
        videos = []

    # Load keywords
    try:
        keywords = db.get_top_keywords(limit=10)
    except Exception:
        keywords = []

    # Load content plans
    try:
        plans = db.get_all_content_plans()
    except Exception:
        plans = []

    # Load scheduled uploads
    try:
        scheduled = db.get_scheduled_uploads()
    except Exception:
        scheduled = []

    # Load channels
    try:
        channels = db.get_all_channels()
    except Exception:
        channels = []

    # Load competitors
    try:
        competitors = db.get_all_competitor_channels()
    except Exception:
        competitors = []

    # Load notifications
    try:
        notifications = db.get_notifications(limit=20)
    except Exception:
        notifications = []

    # Build video rows
    video_rows = ""
    for v in videos:
        title = safe_str(v.get('title_used'), 'Untitled')
        status = safe_str(v.get('status'), 'unknown')
        status_class = status.lower()
        views = safe_int(v.get('views'))
        ctr = safe_float(v.get('ctr'))
        eng = safe_float(v.get('engagement_rate'))
        likes = safe_int(v.get('likes'))
        attempt = safe_int(v.get('attempt_number'), 1)
        max_att = safe_int(v.get('max_attempts'), 3)
        date = safe_str(v.get('upload_date') or v.get('created_at'), '')[:16] or 'Pending'
        video_rows += f"""<tr>
            <td title="{title}">{title[:50]}{'...' if len(title) > 50 else ''}</td>
            <td><span class="badge {status_class}">{status.title()}</span></td>
            <td>{attempt}/{max_att}</td>
            <td>{views:,}</td>
            <td>{ctr:.1f}%</td>
            <td>{eng:.1f}%</td>
            <td>{likes:,}</td>
            <td>{date}</td>
        </tr>"""

    if not video_rows:
        video_rows = '<tr><td colspan="8" class="empty">No videos uploaded yet</td></tr>'

    # Build keyword rows
    kw_rows = ""
    for i, kw in enumerate(keywords):
        kw_rows += f"""<tr>
            <td>#{i+1}</td>
            <td>{kw.get('keyword','')}</td>
            <td>{safe_int(kw.get('video_count'))}</td>
            <td>{safe_int(kw.get('avg_views'))}</td>
            <td>{safe_float(kw.get('avg_ctr')):.1f}%</td>
        </tr>"""

    if not kw_rows:
        kw_rows = '<tr><td colspan="5" class="empty">No keyword data yet</td></tr>'

    # Status breakdown bars
    status_bars = ""
    for s in ['pending', 'uploaded', 'monitoring', 'success', 'retry', 'abandoned']:
        count = by_status.get(s, 0)
        pct = (count / max(total, 1)) * 100
        color_map = {'pending': '#888', 'uploaded': '#2196F3', 'monitoring': '#2196F3',
                     'success': '#4CAF50', 'retry': '#FF9800', 'abandoned': '#f44336'}
        color = color_map.get(s, '#888')
        status_bars += f"""<div class="bar-row">
            <span class="bar-label">{s.title()} ({count})</span>
            <div class="bar-bg"><div class="bar-fill" style="width:{max(pct,1)}%;background:{color}"></div></div>
        </div>"""

    # Plans rows
    plan_rows = ""
    for p in plans[:10]:
        plan_rows += f"""<tr>
            <td>{safe_str(p.get('title'))}</td>
            <td>{safe_str(p.get('niche'))}</td>
            <td>{safe_str(p.get('status'), 'idea').title()}</td>
            <td>{safe_str(p.get('target_date'), '-')}</td>
        </tr>"""
    if not plan_rows:
        plan_rows = '<tr><td colspan="4" class="empty">No content plans yet</td></tr>'

    # Scheduled rows
    sched_rows = ""
    for s in scheduled[:10]:
        sched_rows += f"""<tr>
            <td>{safe_str(s.get('file_path', '')).split('/')[-1]}</td>
            <td>{'Short' if s.get('is_short') else 'Standard'}</td>
            <td>{safe_str(s.get('scheduled_at'))}</td>
            <td><span class="badge {safe_str(s.get('status','queued'))}">{safe_str(s.get('status','queued')).title()}</span></td>
        </tr>"""
    if not sched_rows:
        sched_rows = '<tr><td colspan="4" class="empty">No scheduled uploads</td></tr>'

    # Channels rows
    channel_rows = ""
    for ch in channels:
        default = ' (Default)' if ch.get('is_default') else ''
        channel_rows += f"""<tr>
            <td>{safe_str(ch.get('channel_name'))}{default}</td>
            <td>{safe_str(ch.get('channel_id'))}</td>
        </tr>"""
    if not channel_rows:
        channel_rows = '<tr><td colspan="2" class="empty">No channels registered</td></tr>'

    # Competitor rows
    comp_rows = ""
    for c in competitors:
        comp_rows += f"""<tr>
            <td>{safe_str(c.get('channel_name'))}</td>
            <td>{safe_str(c.get('channel_id'))}</td>
            <td>{safe_int(c.get('subscriber_count')):,}</td>
            <td>{safe_int(c.get('video_count'))}</td>
        </tr>"""
    if not comp_rows:
        comp_rows = '<tr><td colspan="4" class="empty">No competitors tracked</td></tr>'

    # Notifications
    notif_html = ""
    unread = sum(1 for n in notifications if not n.get('is_read'))
    for n in notifications:
        read_class = '' if n.get('is_read') else 'unread'
        notif_html += f"""<div class="notif-card {read_class}">
            <strong>[{safe_str(n.get('type','info')).upper()}]</strong> {safe_str(n.get('title'))}
            <span class="notif-time">{safe_str(n.get('created_at',''))[:16]}</span>
        </div>"""
    if not notif_html:
        notif_html = '<div class="empty-msg">No notifications</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RealE Tube - YouTube Automation Platform</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#0D0D0D; color:#E0E0E0; }}
.header {{ background:#1A1A1A; padding:16px 32px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #FF6B35; }}
.header h1 {{ color:#FF6B35; font-size:24px; }}
.header .status {{ color:#4CAF50; font-size:14px; }}
.nav {{ background:#141414; padding:8px 32px; display:flex; gap:4px; flex-wrap:wrap; border-bottom:1px solid #333; }}
.nav button {{ background:transparent; color:#999; border:none; padding:8px 16px; cursor:pointer; border-radius:6px 6px 0 0; font-size:13px; }}
.nav button:hover {{ background:#222; color:#fff; }}
.nav button.active {{ background:#FF6B35; color:#fff; }}
.container {{ max-width:1400px; margin:0 auto; padding:20px 32px; }}
.tab-content {{ display:none; }}
.tab-content.active {{ display:block; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:24px; }}
.card {{ background:#1A1A1A; border-radius:10px; padding:20px; text-align:center; border:1px solid #333; }}
.card .value {{ font-size:32px; font-weight:bold; color:#FF6B35; }}
.card .label {{ color:#999; font-size:13px; margin-top:4px; }}
.card .desc {{ color:#666; font-size:11px; margin-top:4px; }}
.card .value.green {{ color:#4CAF50; }}
.card .value.blue {{ color:#2196F3; }}
.section {{ background:#1A1A1A; border-radius:10px; padding:20px; margin-bottom:20px; border:1px solid #333; }}
.section h2 {{ color:#FF6B35; font-size:18px; margin-bottom:16px; display:flex; align-items:center; gap:8px; }}
.uc-badge {{ background:#FF9800; color:#fff; font-size:11px; padding:2px 8px; border-radius:10px; cursor:help; }}
table {{ width:100%; border-collapse:collapse; }}
th {{ text-align:left; padding:10px 12px; border-bottom:2px solid #333; color:#999; font-size:12px; text-transform:uppercase; }}
td {{ padding:8px 12px; border-bottom:1px solid #222; font-size:13px; }}
tr:hover {{ background:#222; }}
.empty {{ text-align:center; color:#666; padding:24px !important; }}
.badge {{ padding:3px 10px; border-radius:12px; font-size:11px; font-weight:600; }}
.badge.success {{ background:#1B5E20; color:#4CAF50; }}
.badge.uploaded {{ background:#0D47A1; color:#42A5F5; }}
.badge.monitoring {{ background:#0D47A1; color:#42A5F5; }}
.badge.retry {{ background:#E65100; color:#FF9800; }}
.badge.abandoned {{ background:#B71C1C; color:#EF5350; }}
.badge.pending {{ background:#333; color:#999; }}
.badge.queued {{ background:#333; color:#999; }}
.bar-row {{ display:flex; align-items:center; margin-bottom:8px; }}
.bar-label {{ width:140px; font-size:13px; color:#999; }}
.bar-bg {{ flex:1; background:#222; height:18px; border-radius:4px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:4px; transition:width 0.3s; }}
.notif-card {{ background:#222; border-radius:8px; padding:10px 14px; margin-bottom:8px; font-size:13px; display:flex; justify-content:space-between; }}
.notif-card.unread {{ border-left:3px solid #FF6B35; }}
.notif-time {{ color:#666; font-size:11px; }}
.empty-msg {{ color:#666; text-align:center; padding:20px; }}
.under-construction {{ background:#1A1A1A; border:1px dashed #FF9800; border-radius:10px; padding:32px; text-align:center; color:#999; margin-bottom:20px; }}
.under-construction h3 {{ color:#FF9800; margin-bottom:8px; }}
.grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
@media(max-width:800px) {{ .grid-2 {{ grid-template-columns:1fr; }} .cards {{ grid-template-columns:1fr 1fr; }} }}
.refresh-btn {{ background:#FF6B35; color:#fff; border:none; padding:6px 16px; border-radius:6px; cursor:pointer; font-size:13px; float:right; }}
.refresh-btn:hover {{ background:#E55A25; }}
</style>
</head>
<body>

<div class="header">
    <h1>RealE Tube</h1>
    <span class="status">Web Dashboard Mode</span>
</div>

<div class="nav">
    <button class="active" onclick="showTab('dashboard')">Dashboard</button>
    <button onclick="showTab('videos')">Videos</button>
    <button onclick="showTab('analytics')">Analytics</button>
    <button onclick="showTab('schedule')">Schedule</button>
    <button onclick="showTab('seo')">SEO Score</button>
    <button onclick="showTab('content')">Content Plan</button>
    <button onclick="showTab('competitors')">Competitors</button>
    <button onclick="showTab('channels')">Channels</button>
    <button onclick="showTab('notifications')">Notifications {f'({unread})' if unread else ''}</button>
    <button onclick="showTab('trends')">Trends</button>
    <button onclick="showTab('revenue')">Revenue</button>
    <button onclick="showTab('retention')">Retention</button>
    <button onclick="showTab('shorts')">Shorts</button>
    <button onclick="showTab('abtesting')">A/B Testing</button>
    <button onclick="showTab('predictive')">Predictive</button>
    <button onclick="showTab('lifecycle')">Lifecycle</button>
    <button onclick="showTab('crossplatform')">Cross-Platform</button>
    <button onclick="showTab('collaboration')">Collaboration</button>
</div>

<div class="container">

<!-- DASHBOARD -->
<div id="dashboard" class="tab-content active">
    <div class="cards">
        <div class="card"><div class="value blue">{total}</div><div class="label">Total Videos</div></div>
        <div class="card"><div class="value green">{success_rate:.1f}%</div><div class="label">Success Rate</div></div>
        <div class="card"><div class="value">{avg_attempts:.1f}</div><div class="label">Avg Attempts</div></div>
        <div class="card"><div class="value">{by_status.get('retry',0)}</div><div class="label">In Retry</div></div>
        <div class="card"><div class="value" style="color:#f44336">{by_status.get('abandoned',0)}</div><div class="label">Abandoned</div></div>
    </div>
    <div class="section">
        <h2>Status Breakdown</h2>
        {status_bars}
    </div>
</div>

<!-- VIDEOS -->
<div id="videos" class="tab-content">
    <div class="section">
        <h2>Video Tracking <a href="/" class="refresh-btn">Refresh</a></h2>
        <table>
            <thead><tr><th>Title</th><th>Status</th><th>Attempt</th><th>Views</th><th>CTR</th><th>Engagement</th><th>Likes</th><th>Uploaded</th></tr></thead>
            <tbody>{video_rows}</tbody>
        </table>
    </div>
</div>

<!-- ANALYTICS -->
<div id="analytics" class="tab-content">
    <div class="cards">
        <div class="card"><div class="value green">{success_rate:.1f}%</div><div class="label">Success Rate</div></div>
        <div class="card"><div class="value">{avg_attempts:.1f}</div><div class="label">Avg Attempts</div></div>
        <div class="card"><div class="value blue">{total}</div><div class="label">Total Videos</div></div>
    </div>
    <div class="section">
        <h2>Best Performing Keywords</h2>
        <table>
            <thead><tr><th>#</th><th>Keyword</th><th>Videos</th><th>Avg Views</th><th>Avg CTR</th></tr></thead>
            <tbody>{kw_rows}</tbody>
        </table>
    </div>
</div>

<!-- SCHEDULE -->
<div id="schedule" class="tab-content">
    <div class="section">
        <h2>Upload Schedule & Queue <span class="uc-badge" title="This feature is under construction">?</span></h2>
        <table>
            <thead><tr><th>File</th><th>Type</th><th>Scheduled</th><th>Status</th></tr></thead>
            <tbody>{sched_rows}</tbody>
        </table>
    </div>
</div>

<!-- SEO SCORE -->
<div id="seo" class="tab-content">
    <div class="section">
        <h2>SEO Score Card</h2>
        <p style="color:#999;margin-bottom:16px">Select a video from the Videos tab to analyze its SEO score. Manual scoring available in the desktop app.</p>
        <div class="cards">
            <div class="card"><div class="value">--</div><div class="label">Title Score</div><div class="desc">Length, power words, numbers</div></div>
            <div class="card"><div class="value">--</div><div class="label">Description Score</div><div class="desc">Length, links, timestamps</div></div>
            <div class="card"><div class="value">--</div><div class="label">Tags Score</div><div class="desc">Count, long-tail, uniqueness</div></div>
            <div class="card"><div class="value">--</div><div class="label">Overall Score</div><div class="desc">Weighted average</div></div>
        </div>
    </div>
</div>

<!-- CONTENT PLAN -->
<div id="content" class="tab-content">
    <div class="section">
        <h2>AI Content Planner <span class="uc-badge" title="This feature is under construction">?</span></h2>
        <table>
            <thead><tr><th>Title</th><th>Niche</th><th>Status</th><th>Target Date</th></tr></thead>
            <tbody>{plan_rows}</tbody>
        </table>
    </div>
</div>

<!-- COMPETITORS -->
<div id="competitors" class="tab-content">
    <div class="section">
        <h2>Competitor Tracking <span class="uc-badge" title="This feature is under construction">?</span></h2>
        <table>
            <thead><tr><th>Channel</th><th>Channel ID</th><th>Subscribers</th><th>Videos</th></tr></thead>
            <tbody>{comp_rows}</tbody>
        </table>
    </div>
</div>

<!-- CHANNELS -->
<div id="channels" class="tab-content">
    <div class="section">
        <h2>Multi-Channel Management <span class="uc-badge" title="This feature is under construction">?</span></h2>
        <table>
            <thead><tr><th>Channel Name</th><th>Channel ID</th></tr></thead>
            <tbody>{channel_rows}</tbody>
        </table>
    </div>
</div>

<!-- NOTIFICATIONS -->
<div id="notifications" class="tab-content">
    <div class="section">
        <h2>Notifications & Alerts</h2>
        {notif_html}
    </div>
</div>

<!-- TRENDS -->
<div id="trends" class="tab-content">
    <div class="under-construction">
        <h3>Trend Detection & Niche Alerts <span class="uc-badge">?</span></h3>
        <p>Connect Google Trends API in Settings to enable live trend detection.</p>
    </div>
</div>

<!-- REVENUE -->
<div id="revenue" class="tab-content">
    <div class="under-construction">
        <h3>Revenue & CPM Analytics <span class="uc-badge">?</span></h3>
        <p>Connect YouTube Analytics API to enable revenue tracking. Requires YouTube Partner Program membership.</p>
    </div>
    <div class="cards">
        <div class="card"><div class="value">$0.00</div><div class="label">Est. Revenue</div></div>
        <div class="card"><div class="value">$0.00</div><div class="label">Avg CPM</div></div>
        <div class="card"><div class="value">$0.00</div><div class="label">Avg RPM</div></div>
        <div class="card"><div class="value">0</div><div class="label">Monetized Views</div></div>
    </div>
</div>

<!-- RETENTION -->
<div id="retention" class="tab-content">
    <div class="under-construction">
        <h3>Audience Retention Analysis <span class="uc-badge">?</span></h3>
        <p>Connect YouTube Analytics API to enable retention heatmaps.</p>
    </div>
</div>

<!-- SHORTS -->
<div id="shorts" class="tab-content">
    <div class="section">
        <h2>Shorts Pipeline <span class="uc-badge" title="This feature is under construction">?</span></h2>
        <p style="color:#999">Queue vertical videos under 60 seconds with optimized Shorts metadata. Shorts use a different keyword and discovery strategy.</p>
    </div>
</div>

<!-- A/B TESTING -->
<div id="abtesting" class="tab-content">
    <div class="under-construction">
        <h3>A/B Thumbnail Testing <span class="uc-badge">?</span></h3>
        <p>Upload thumbnail variants, track CTR per variant, auto-select winners.</p>
    </div>
</div>

<!-- PREDICTIVE -->
<div id="predictive" class="tab-content">
    <div class="under-construction">
        <h3>Predictive Performance <span class="uc-badge">?</span></h3>
        <p>ML-based view prediction using historical keyword and metadata correlations. Requires sufficient training data.</p>
        <p style="margin-top:8px">Training data: <strong>{len(videos)} videos</strong> in database</p>
    </div>
</div>

<!-- LIFECYCLE -->
<div id="lifecycle" class="tab-content">
    <div class="section">
        <h2>Content Lifecycle <span class="uc-badge" title="This feature is under construction">?</span></h2>
        <p style="color:#999">Track evergreen content, identify re-optimization candidates, manage video age breakdown.</p>
    </div>
</div>

<!-- CROSS-PLATFORM -->
<div id="crossplatform" class="tab-content">
    <div class="under-construction">
        <h3>Cross-Platform Publishing <span class="uc-badge">?</span></h3>
        <p>Publish to YouTube, TikTok, Instagram Reels, and X/Twitter from one interface.</p>
        <div class="cards" style="margin-top:16px">
            <div class="card"><div class="value" style="font-size:20px">YouTube</div><div class="desc">Active</div></div>
            <div class="card"><div class="value" style="font-size:20px">TikTok</div><div class="desc">Not Connected</div></div>
            <div class="card"><div class="value" style="font-size:20px">Instagram</div><div class="desc">Not Connected</div></div>
            <div class="card"><div class="value" style="font-size:20px">X/Twitter</div><div class="desc">Not Connected</div></div>
        </div>
    </div>
</div>

<!-- COLLABORATION -->
<div id="collaboration" class="tab-content">
    <div class="under-construction">
        <h3>Collaborative Workspaces <span class="uc-badge">?</span></h3>
        <p>Team roles: Owner, Editor, Uploader, Analyst, Viewer. Cloud auth infrastructure coming soon.</p>
    </div>
</div>

</div>

<script>
function showTab(id) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav button').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.target.classList.add('active');
}}
</script>
</body>
</html>"""


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(get_dashboard_html().encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Suppress request logs


if __name__ == '__main__':
    print("=" * 50)
    print("  RealE Tube - Web Dashboard")
    print("  Copyright (c) 2024 RealE Technology Solutions")
    print("=" * 50)
    print(f"\n  Open in your browser: http://localhost:{PORT}\n")
    print("  Press Ctrl+C to stop\n")

    # Don't open browser if launched by Electron or with --no-browser
    if '--no-browser' not in sys.argv and not os.environ.get('ELECTRON_MODE'):
        try:
            import webbrowser
            webbrowser.open(f'http://localhost:{PORT}')
        except Exception:
            pass

    server = http.server.HTTPServer(('', PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
