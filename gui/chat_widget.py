# -*- coding: utf-8 -*-
"""
RealE Tube - Floating Chat Assistant Widget

A CTkToplevel window that hosts the conversational assistant. The agent runs
on a background thread so the Tk main loop stays responsive; every UI update
is marshalled back via `after(0, …)`.

The widget renders:
  • Scrollable message history (user / agent / system)
  • An input box + send button
  • Clickable "quick reply" chips that the agent suggests

Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import List, Optional

import customtkinter as ctk

from automation.chat_agent import ChatAgent, ChatController


class ChatWidget(ctk.CTkToplevel):
    """Floating, always-available chat window for the RealE Tube assistant."""

    WINDOW_WIDTH = 440
    WINDOW_HEIGHT = 560

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.theme = app.theme_config

        self.title("RealE Assistant")
        self._position_near_parent()
        self.minsize(360, 420)
        self.configure(fg_color=self.theme["bg_primary"])

        # Don't kill the whole app — just hide the window so it can be reopened.
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Agent state — may be None until credentials are available.
        self.agent: Optional[ChatAgent] = None
        self._pending = False
        self._quick_reply_buttons: List[ctk.CTkButton] = []

        self._build_ui()
        self._initialise_agent()
        self._greet()

    # ── Layout ──────────────────────────────────────────────────────

    def _position_near_parent(self) -> None:
        try:
            self.app.update_idletasks()
            px = self.app.winfo_rootx()
            py = self.app.winfo_rooty()
            pw = self.app.winfo_width()
            ph = self.app.winfo_height()
            x = px + pw - self.WINDOW_WIDTH - 30
            y = py + ph - self.WINDOW_HEIGHT - 30
            self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

    def _build_ui(self) -> None:
        t = self.theme

        # Header
        header = ctk.CTkFrame(self, fg_color=t["bg_secondary"], corner_radius=0, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="RealE Assistant",
            font=(t["font_family"], t["font_size_body"], "bold"),
            text_color=t["text_primary"],
        ).pack(side="left", padx=14, pady=10)

        ctk.CTkButton(
            header, text="New chat", width=82, height=28, corner_radius=6,
            font=(t["font_family"], t["font_size_small"]),
            fg_color=t["bg_tertiary"], hover_color=t["button_hover"],
            text_color=t["text_primary"],
            command=self._reset_chat,
        ).pack(side="right", padx=10, pady=10)

        # Messages area
        self.messages_frame = ctk.CTkScrollableFrame(self, fg_color=t["bg_primary"])
        self.messages_frame.pack(fill="both", expand=True, padx=10, pady=(8, 0))

        # Quick replies
        self.quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quick_frame.pack(fill="x", padx=10, pady=(6, 0))

        # Input row
        input_row = ctk.CTkFrame(self, fg_color="transparent")
        input_row.pack(fill="x", padx=10, pady=10)

        self.input_box = ctk.CTkEntry(
            input_row,
            placeholder_text="Ask me anything about RealE Tube…",
            fg_color=t["input_bg"], border_color=t["input_border"],
            text_color=t["text_primary"],
            font=(t["font_family"], t["font_size_body"]),
            height=36,
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_box.bind("<Return>", lambda _e: self._send())

        self.send_btn = ctk.CTkButton(
            input_row, text="Send", width=74, height=36, corner_radius=8,
            font=(t["font_family"], t["font_size_body"]),
            fg_color=t["accent"], hover_color=t["accent_hover"],
            text_color="#FFFFFF",
            command=self._send,
        )
        self.send_btn.pack(side="left")

    # ── Agent wiring ────────────────────────────────────────────────

    def _initialise_agent(self) -> None:
        try:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
            if not config_path.exists():
                return
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            api_key = config.get("api", {}).get("ai_api_key", "")
            if not api_key:
                return
            controller = ChatController(self.app, config_path)
            self.agent = ChatAgent(api_key, controller)
        except Exception as e:  # noqa: BLE001
            self._append_message("system", f"Couldn't initialise assistant: {e}")

    # ── Rendering ───────────────────────────────────────────────────

    def _greet(self) -> None:
        if self.agent is None:
            self._append_message(
                "system",
                "Add your Claude API key in Settings → API Configuration, "
                "then reopen this window to start chatting.",
            )
            self._render_quick_replies(["Open Settings"])
            return

        self._append_message(
            "agent",
            "Hi! I can tweak settings, explain features, find reopt candidates, "
            "analyse timing, and navigate the app for you. What's on your mind?",
        )
        self._render_quick_replies([
            "Find reopt candidates",
            "Analyse best posting times",
            "Set competitor max age to 90 days",
            "Show automation status",
        ])

    def _append_message(self, role: str, text: str) -> None:
        t = self.theme
        if role == "user":
            fg = t["accent"]
            fg_text = "#FFFFFF"
            anchor = "e"
            justify = "right"
        elif role == "agent":
            fg = t["bg_secondary"]
            fg_text = t["text_primary"]
            anchor = "w"
            justify = "left"
        else:  # system
            fg = t["bg_tertiary"]
            fg_text = t["text_tertiary"]
            anchor = "w"
            justify = "left"

        row = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        row.pack(fill="x", pady=4)

        bubble = ctk.CTkLabel(
            row,
            text=text,
            font=(t["font_family"], t["font_size_body"]),
            fg_color=fg,
            text_color=fg_text,
            corner_radius=10,
            padx=12, pady=8,
            justify=justify,
            wraplength=self.WINDOW_WIDTH - 80,
            anchor=anchor,
        )
        bubble.pack(anchor=anchor)

        # Autoscroll
        self.after(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        try:
            canvas = getattr(self.messages_frame, "_parent_canvas", None)
            if canvas is not None:
                canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _render_quick_replies(self, suggestions: List[str]) -> None:
        for btn in self._quick_reply_buttons:
            btn.destroy()
        self._quick_reply_buttons = []

        if not suggestions:
            return

        t = self.theme
        for text in suggestions:
            btn = ctk.CTkButton(
                self.quick_frame,
                text=text,
                font=(t["font_family"], t["font_size_small"]),
                fg_color=t["bg_tertiary"],
                hover_color=t["button_hover"],
                text_color=t["text_primary"],
                corner_radius=14, height=28,
                command=lambda txt=text: self._quick_reply(txt),
            )
            # Pack chips horizontally, wrapping via multiple rows is not trivial
            # in classic Tk — fine for a narrow column of 4 chips.
            btn.pack(side="top", anchor="w", pady=2)
            self._quick_reply_buttons.append(btn)

    # ── Interaction ─────────────────────────────────────────────────

    def _quick_reply(self, text: str) -> None:
        # Special-case the "open settings" chip when the agent isn't ready yet.
        if self.agent is None and text.lower() == "open settings":
            try:
                self.app._switch_tab("settings")
            except Exception:
                pass
            return
        self.input_box.delete(0, "end")
        self.input_box.insert(0, text)
        self._send()

    def _send(self) -> None:
        if self._pending:
            return
        text = self.input_box.get().strip()
        if not text:
            return
        if self.agent is None:
            self._append_message("system", "Assistant isn't configured — add a Claude API key first.")
            return

        self.input_box.delete(0, "end")
        self._append_message("user", text)
        self._render_quick_replies([])
        self._set_pending(True)

        threading.Thread(target=self._run_agent, args=(text,), daemon=True).start()

    def _run_agent(self, user_text: str) -> None:
        try:
            result = self.agent.send(user_text)
        except Exception as e:  # noqa: BLE001
            result = {"reply": f"(Error: {e})", "actions": [], "suggestions": [], "error": str(e)}
        # Hop back to the Tk main thread.
        self.after(0, lambda: self._on_agent_result(result))

    def _on_agent_result(self, result: dict) -> None:
        reply = result.get("reply") or "(No response.)"
        self._append_message("agent", reply)

        # Show a compact breadcrumb for any tool actions the agent took.
        actions = result.get("actions") or []
        if actions:
            summary = _summarise_actions(actions)
            if summary:
                self._append_message("system", summary)

        self._render_quick_replies(result.get("suggestions") or [])
        self._set_pending(False)

    def _set_pending(self, pending: bool) -> None:
        self._pending = pending
        state = "disabled" if pending else "normal"
        self.input_box.configure(state=state)
        self.send_btn.configure(
            state=state,
            text="…" if pending else "Send",
        )

    def _reset_chat(self) -> None:
        if self.agent is not None:
            self.agent.reset()
        for child in self.messages_frame.winfo_children():
            child.destroy()
        self._render_quick_replies([])
        self._greet()

    def _on_close(self) -> None:
        # Hide instead of destroying so the same instance can be reused.
        self.withdraw()


def _summarise_actions(actions: List[dict]) -> str:
    """One-line breadcrumb of tool calls the agent made, for transparency."""
    parts: List[str] = []
    for a in actions:
        name = a.get("name")
        inp = a.get("input") or {}
        if name == "switch_tab":
            parts.append(f"→ Switched to {inp.get('tab_key')}")
        elif name == "set_config":
            parts.append(f"⚙ Updated {inp.get('section')}.{inp.get('key')}")
        elif name == "get_config":
            parts.append(f"· Read {inp.get('section')}.{inp.get('key')}")
        elif name == "start_automation":
            parts.append("▶ Started automation")
        elif name == "stop_automation":
            parts.append("■ Stopped automation")
        elif name == "find_reopt_candidates":
            parts.append("· Checked reopt candidates")
        elif name == "analyze_timing":
            parts.append("· Analysed posting times")
        elif name == "list_competitors":
            parts.append("· Listed competitors")
        elif name == "get_status":
            parts.append("· Checked status")
    return "  ".join(parts)
