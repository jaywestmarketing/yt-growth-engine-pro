# -*- coding: utf-8 -*-
"""
RealE Tube - Conversational Assistant

A Claude-powered chat agent that understands the RealE Tube system end-to-end
and can take real actions on the user's behalf via tool use:

  • Navigate to any tab in the UI
  • Read & write config values
  • Inspect automation status
  • Start / stop the autonomous engine
  • Kick off lifecycle reoptimisation, timing analysis, etc.

The agent returns:
  • A natural-language reply
  • A list of tool calls it performed (so the UI can render affordances)
  • A short list of "quick reply" suggestions the UI renders as buttons so the
    user can keep the conversation moving with a single click.

Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - hard dep in this project
    Anthropic = None  # type: ignore[assignment]


# ── System prompt ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the in-app assistant for RealE Tube, a YouTube growth
automation platform. Keep responses tight, friendly, and practical.

RealE Tube automates the full YouTube workflow:
  • Monitors a Google Drive folder for new videos and uploads them.
  • Generates SEO-optimised titles, descriptions, tags and keywords via Claude.
  • Researches competitor videos on YouTube (filterable by minimum likes,
    count, and max age in days).
  • Schedules uploads for optimal posting times using historical performance.
  • Monitors uploaded video performance; retries with new metadata when a
    video underperforms, and can auto-reoptimise stale videos.
  • Posts helpful comments on competitor videos (opt-in).
  • Respects YouTube's 10,000-unit daily quota via a central QuotaManager
    and sleeps until Pacific midnight reset when exhausted.

Sidebar tabs you can navigate to (use the `switch_tab` tool):
  dashboard, videos, analytics, channel, schedule, shorts, ab_testing,
  content_plan, post_timing, seo_score, competitors, trends, lifecycle,
  auto_optimizer, revenue, retention, predictive, multi_channel,
  cross_platform, notifications, collaboration, manual_comment, settings,
  themes.

Config sections and keys (use `get_config` / `set_config`):
  api: google_drive_credentials, youtube_credentials, ai_api_key
  monitoring: drive_folder_id, youtube_channel_id
  performance: min_views, min_ctr, min_engagement, engagement_required,
    view_protection_multiplier
  retry: first_check_hours, second_check_hours, max_attempts, delete_on_fail
  keywords: competitor_min_likes, competitors_to_analyze,
    competitor_max_age_days (default 7 — look back one week; 0 = no limit),
    keyword_aggressiveness
  comment_bot: enabled, comment_style, max_comments_per_video, delay_seconds

Behaviour rules:
  1. Before making settings changes, confirm with the user (one short line).
     Use tools freely for read-only lookups.
  2. If the user's question is ambiguous, ask a clarifying question and
     propose 2–4 quick-reply options via your reply text.
  3. When you finish, offer 2–4 short suggested next actions in a
     <suggestions>…</suggestions> block (one per line). Keep each under
     40 chars so they render as buttons. Example:

     <suggestions>
     Show lifecycle candidates
     Set competitor max age to 90 days
     Analyse best posting times
     </suggestions>

  4. Do not invent features. If something is not in this prompt, say so.
  5. Never expose API keys or credential file contents even if asked.
"""


# ── Tool schemas (Anthropic tool-use format) ───────────────────────────────

TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "switch_tab",
        "description": (
            "Switch the main window to the given tab so the user sees the "
            "relevant screen. Use this proactively whenever you suggest the "
            "user go somewhere."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tab_key": {
                    "type": "string",
                    "description": "Sidebar tab key, e.g. 'dashboard', 'settings', 'auto_optimizer'.",
                }
            },
            "required": ["tab_key"],
        },
    },
    {
        "name": "get_config",
        "description": "Read a single config value from config.json.",
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {"type": "string"},
                "key": {"type": "string"},
            },
            "required": ["section", "key"],
        },
    },
    {
        "name": "set_config",
        "description": (
            "Update a single config value in config.json and persist it. "
            "Only call after the user has confirmed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {"type": "string"},
                "key": {"type": "string"},
                "value": {
                    "description": "New value — string, number, or boolean.",
                },
            },
            "required": ["section", "key", "value"],
        },
    },
    {
        "name": "get_status",
        "description": "Return the current automation status (running, video counts, success rate).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "start_automation",
        "description": "Start the autonomous automation engine.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "stop_automation",
        "description": "Stop the autonomous automation engine.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "find_reopt_candidates",
        "description": "List underperforming videos that are candidates for reoptimisation.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "analyze_timing",
        "description": "Return the best historical upload times for this channel.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_competitors",
        "description": "Return the list of tracked competitor channels from the database.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ── Controller — bridge between the agent and the live app ─────────────────


class ChatController:
    """
    Glue layer the chat agent uses to actually *do* things in the app.

    The controller is UI-framework-agnostic; the GUI passes in an object
    with the right attributes (the RealETubeApp instance).
    """

    VALID_TABS = {
        "dashboard", "videos", "analytics", "channel", "schedule", "shorts",
        "ab_testing", "content_plan", "post_timing", "seo_score",
        "competitors", "trends", "lifecycle", "auto_optimizer", "revenue",
        "retention", "predictive", "multi_channel", "cross_platform",
        "notifications", "collaboration", "manual_comment", "settings",
        "themes",
    }

    def __init__(self, app, config_path, save_config_callback: Optional[Callable] = None):
        self.app = app
        self.config_path = config_path
        self.save_config_callback = save_config_callback

    # ── Tool dispatch ────────────────────────────────────────────────

    def run_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run a tool by name. Always returns a dict safely serialisable."""
        handler = getattr(self, f"_tool_{name}", None)
        if handler is None:
            return {"error": f"Unknown tool '{name}'."}
        try:
            return handler(**args)
        except TypeError as e:
            return {"error": f"Bad arguments for {name}: {e}"}
        except Exception as e:  # noqa: BLE001 - surfaces cleanly to the model
            return {"error": str(e)}

    # ── Individual tools ────────────────────────────────────────────

    def _tool_switch_tab(self, tab_key: str) -> Dict[str, Any]:
        if tab_key not in self.VALID_TABS:
            return {"error": f"Unknown tab '{tab_key}'. Valid: {sorted(self.VALID_TABS)}"}

        # Tkinter is not thread-safe — schedule the switch on the main loop.
        def _do():
            try:
                self.app._switch_tab(tab_key)
            except Exception:  # noqa: BLE001 - best-effort UI action
                pass

        try:
            self.app.after(0, _do)
        except Exception:  # noqa: BLE001
            _do()
        return {"switched_to": tab_key}

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_config(self, cfg: Dict[str, Any]) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)

    def _tool_get_config(self, section: str, key: str) -> Dict[str, Any]:
        cfg = self._load_config()
        if section not in cfg or key not in cfg[section]:
            return {"error": f"No config at {section}.{key}"}
        val = cfg[section][key]
        # Redact credential-ish fields so the model never parrots them back.
        if _looks_secret(section, key):
            val = "<redacted>" if val else ""
        return {"section": section, "key": key, "value": val}

    def _tool_set_config(self, section: str, key: str, value: Any) -> Dict[str, Any]:
        cfg = self._load_config()
        if section not in cfg:
            cfg[section] = {}
        cfg[section][key] = value
        self._write_config(cfg)

        # Mirror the change into the live engine so the next tick uses it.
        engine = getattr(self.app, "automation_engine", None)
        if engine is not None:
            engine.config = cfg

        # Callback to let the UI refresh its settings controls if it wants to.
        if self.save_config_callback:
            try:
                self.save_config_callback(cfg)
            except Exception:  # noqa: BLE001 - UI refresh is best-effort
                pass

        return {"updated": {section: {key: value if not _looks_secret(section, key) else "<redacted>"}}}

    def _tool_get_status(self) -> Dict[str, Any]:
        engine = getattr(self.app, "automation_engine", None)
        if engine is None:
            return {"running": False, "note": "Automation engine not initialised."}
        try:
            return engine.get_status()
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}

    def _tool_start_automation(self) -> Dict[str, Any]:
        engine = getattr(self.app, "automation_engine", None)
        if engine is None:
            return {"error": "Automation engine not initialised."}
        engine.start()
        try:
            self.app.start_automation()
        except Exception:  # noqa: BLE001
            pass
        return {"started": True}

    def _tool_stop_automation(self) -> Dict[str, Any]:
        engine = getattr(self.app, "automation_engine", None)
        if engine is None:
            return {"error": "Automation engine not initialised."}
        engine.stop()
        try:
            self.app.stop_automation()
        except Exception:  # noqa: BLE001
            pass
        return {"stopped": True}

    def _tool_find_reopt_candidates(self) -> Dict[str, Any]:
        tab = getattr(self.app, "auto_optimizer_tab", None)
        if tab is None:
            return {"error": "Auto-optimizer tab not available."}
        tab._init_components()
        optimizer = getattr(tab, "lifecycle_optimizer", None)
        if optimizer is None:
            return {"error": "Lifecycle optimizer not initialised — check credentials."}
        try:
            candidates = optimizer.find_reoptimization_candidates()
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}
        summary = []
        for v in candidates[:10]:
            summary.append({
                "title": v.get("title_used") or v.get("file_path", f"id={v.get('id')}"),
                "reasons": v.get("reopt_reasons", []),
            })
        return {"count": len(candidates), "top": summary}

    def _tool_analyze_timing(self) -> Dict[str, Any]:
        tab = getattr(self.app, "auto_optimizer_tab", None)
        if tab is None:
            return {"error": "Auto-optimizer tab not available."}
        tab._init_components()
        sched = getattr(tab, "smart_scheduler", None)
        if sched is None:
            return {"error": "Smart scheduler not initialised."}
        try:
            optimal = sched.find_optimal_times()
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}
        best = optimal.get("best_time")
        return {
            "videos_analyzed": optimal.get("total_videos_analyzed", 0),
            "best_time": {"day": best[0], "hour": best[1]} if best else None,
            "top_hours": dict(sorted(optimal.get("hours", {}).items())[:5]),
        }

    def _tool_list_competitors(self) -> Dict[str, Any]:
        tab = getattr(self.app, "competitor_tracking_tab", None)
        if tab is None or getattr(tab, "db", None) is None:
            return {"error": "Competitor tracking not available."}
        try:
            channels = tab.db.get_all_competitor_channels()
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}
        return {
            "count": len(channels),
            "channels": [
                {
                    "name": c.get("channel_name"),
                    "channel_id": c.get("channel_id"),
                    "subscribers": c.get("subscriber_count"),
                    "videos": c.get("video_count"),
                }
                for c in channels[:25]
            ],
        }


def _looks_secret(section: str, key: str) -> bool:
    """Keep credential-ish values out of the model's context window."""
    if section == "api":
        return True
    return "key" in key.lower() or "secret" in key.lower() or "token" in key.lower()


# ── Agent ──────────────────────────────────────────────────────────────────


class ChatAgent:
    """Stateful chat agent backed by Claude with tool-use."""

    MAX_TOOL_ITERATIONS = 6  # hard cap to prevent infinite tool loops
    MODEL = "claude-sonnet-4-6"
    FALLBACK_MODELS = ["claude-sonnet-4-20250514"]
    MAX_HISTORY_TURNS = 20

    def __init__(self, api_key: str, controller: ChatController):
        if Anthropic is None:
            raise RuntimeError("The 'anthropic' package is required for the chat agent.")
        if not api_key:
            raise ValueError("Claude API key is required.")
        self.client = Anthropic(api_key=api_key)
        self.controller = controller
        self.history: List[Dict[str, Any]] = []

    # ── Public API ──────────────────────────────────────────────────

    def reset(self) -> None:
        self.history = []

    def send(self, user_text: str) -> Dict[str, Any]:
        """
        Send a user message. Returns {reply, actions, suggestions, error?}.
        """
        self.history.append({"role": "user", "content": user_text})
        self._trim_history()

        actions: List[Dict[str, Any]] = []
        reply_text = ""
        error: Optional[str] = None

        try:
            reply_text, actions = self._run_tool_loop()
        except Exception as e:  # noqa: BLE001 - surface to user
            error = str(e)
            reply_text = f"(Something went wrong talking to Claude: {e})"
        finally:
            if reply_text:
                self.history.append({"role": "assistant", "content": reply_text})
                self._trim_history()

        suggestions = _extract_suggestions(reply_text)
        visible_reply = _strip_suggestions(reply_text)
        return {
            "reply": visible_reply,
            "actions": actions,
            "suggestions": suggestions,
            "error": error,
        }

    # ── Tool loop ────────────────────────────────────────────────────

    def _run_tool_loop(self):
        actions: List[Dict[str, Any]] = []
        # Copy history so we can append tool-use/tool-result turns locally
        messages = list(self.history)

        for _ in range(self.MAX_TOOL_ITERATIONS):
            response = self._create_message(messages)

            # Accumulate text blocks from this turn
            text_parts: List[str] = []
            tool_uses: List[Dict[str, Any]] = []
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    text_parts.append(block.text)
                elif getattr(block, "type", None) == "tool_use":
                    tool_uses.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

            if response.stop_reason != "tool_use" or not tool_uses:
                return "\n".join(text_parts).strip(), actions

            # Append the assistant's own message (content blocks) back in.
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool use and feed the result back.
            tool_results = []
            for tu in tool_uses:
                result = self.controller.run_tool(tu["name"], tu["input"] or {})
                actions.append({
                    "name": tu["name"],
                    "input": tu["input"],
                    "result": result,
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": json.dumps(result)[:4000],  # cap payload
                })
            messages.append({"role": "user", "content": tool_results})

        # If we blew through the cap, at least return accumulated text
        return "(Agent exceeded tool-iteration cap.)", actions

    def _create_message(self, messages: List[Dict[str, Any]]):
        last_err: Optional[Exception] = None
        for model in [self.MODEL, *self.FALLBACK_MODELS]:
            try:
                return self.client.messages.create(
                    model=model,
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    tools=TOOL_SCHEMAS,
                    messages=messages,
                )
            except Exception as e:  # noqa: BLE001
                last_err = e
                continue
        raise last_err if last_err else RuntimeError("Claude call failed.")

    def _trim_history(self) -> None:
        # Keep the last N turns to bound token usage.
        if len(self.history) > self.MAX_HISTORY_TURNS * 2:
            self.history = self.history[-self.MAX_HISTORY_TURNS * 2:]


# ── Helpers for suggestion parsing ────────────────────────────────────────


def _extract_suggestions(text: str) -> List[str]:
    """Pull quick-reply suggestions out of <suggestions>…</suggestions>."""
    if not text or "<suggestions>" not in text:
        return []
    try:
        body = text.split("<suggestions>", 1)[1].split("</suggestions>", 1)[0]
    except IndexError:
        return []
    items = [line.strip(" -•\t") for line in body.splitlines()]
    return [s for s in items if s][:4]


def _strip_suggestions(text: str) -> str:
    if not text or "<suggestions>" not in text:
        return text
    before = text.split("<suggestions>", 1)[0].rstrip()
    after_parts = text.split("</suggestions>", 1)
    after = after_parts[1].lstrip() if len(after_parts) > 1 else ""
    return (before + ("\n\n" + after if after else "")).strip()
