"""
RealE Tube - Tooltip Utility
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

import customtkinter as ctk
import tkinter as tk


class ToolTip:
    """Hover tooltip for any tkinter/customtkinter widget."""

    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._tip_window = None
        self._after_id = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        self._after_id = self.widget.after(self.delay, self._show)

    def _on_leave(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self):
        if self._tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self._tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#333333",
            foreground="#FFFFFF",
            relief="solid",
            borderwidth=1,
            font=("Helvetica", 11),
            padx=10,
            pady=6,
            wraplength=320,
        )
        label.pack()

    def _hide(self):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


def under_construction_badge(parent, theme, text="This feature is under construction"):
    """Create a small '?' label with an 'under construction' hover tooltip.

    Returns the label widget so it can be packed/gridded by the caller.
    """
    badge = ctk.CTkLabel(
        parent,
        text=" ? ",
        font=(theme["font_family"], 13, "bold"),
        text_color="#FFFFFF",
        fg_color=theme["warning"],
        corner_radius=10,
        width=24,
        height=24,
    )
    ToolTip(badge, text)
    return badge
