"""UI utility functions and helper classes"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from .ui_constants import COLORS, FONTS, TOOLTIPS


class ToolTip:
    """
    Tooltip widget that shows helpful text when hovering over a widget

    Usage:
        ToolTip(widget, "This is a tooltip message")
    """

    def __init__(self, widget, text: str, delay: int = 500):
        """
        Initialize tooltip

        Args:
            widget: Widget to attach tooltip to
            text: Text to display in tooltip
            delay: Delay in milliseconds before showing tooltip
        """
        self.widget = widget
        # Strip whitespace and ensure text is valid
        self.text = text.strip() if text else ""
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None

        # Only bind events if we have valid text
        if self.text:
            self.widget.bind('<Enter>', self._on_enter)
            self.widget.bind('<Leave>', self._on_leave)
            self.widget.bind('<Button>', self._on_leave)

    def _on_enter(self, event=None):
        """Handle mouse enter event"""
        self._schedule_show()

    def _on_leave(self, event=None):
        """Handle mouse leave event"""
        self._cancel_show()
        self._hide()

    def _schedule_show(self):
        """Schedule tooltip to be shown after delay"""
        self._cancel_show()
        self.after_id = self.widget.after(self.delay, self._show)

    def _cancel_show(self):
        """Cancel scheduled tooltip show"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def _show(self):
        """Show the tooltip"""
        if self.tooltip_window or not self.text:
            return

        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Create label with text
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=FONTS['small'],
            padx=5,
            pady=3
        )
        label.pack()

    def _hide(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def create_button_with_icon(parent, text: str, icon: str, command: Callable,
                           tooltip: Optional[str] = None, **kwargs) -> ttk.Button:
    """
    Create a button with icon and tooltip

    Args:
        parent: Parent widget
        text: Button text
        icon: Icon emoji
        command: Button command
        tooltip: Tooltip text (optional)
        **kwargs: Additional button arguments

    Returns:
        Created button widget
    """
    button_text = f"{icon} {text}" if icon else text
    button = ttk.Button(parent, text=button_text, command=command, **kwargs)

    if tooltip:
        ToolTip(button, tooltip)

    return button


def set_status_color(label: ttk.Label, status_type: str):
    """
    Set label color based on status type

    Args:
        label: Label widget to style
        status_type: Type of status ('success', 'warning', 'error', 'info', 'default')
    """
    color = COLORS.get(status_type, COLORS['default'])
    label.configure(foreground=color)


def create_labeled_entry(parent, label_text: str, row: int, tooltip: Optional[str] = None,
                         **entry_kwargs) -> tuple[ttk.Label, ttk.Entry]:
    """
    Create a labeled entry field with optional tooltip

    Args:
        parent: Parent widget
        label_text: Label text
        row: Grid row
        tooltip: Tooltip text (optional)
        **entry_kwargs: Additional entry arguments

    Returns:
        Tuple of (label, entry) widgets
    """
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)

    entry = ttk.Entry(parent, **entry_kwargs)
    entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

    if tooltip:
        ToolTip(label, tooltip)
        ToolTip(entry, tooltip)

    return label, entry


def create_separator(parent, row: int, pady: int = 10):
    """
    Create a horizontal separator

    Args:
        parent: Parent widget
        row: Grid row
        pady: Vertical padding
    """
    separator = ttk.Separator(parent, orient='horizontal')
    separator.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=pady)
    return separator


class StatusBar:
    """Enhanced status bar with multiple sections"""

    def __init__(self, parent):
        """
        Initialize status bar

        Args:
            parent: Parent widget
        """
        self.frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        self.frame.columnconfigure(0, weight=1)

        # Main status label (left)
        self.status_label = ttk.Label(
            self.frame,
            text="Ready",
            anchor=tk.W,
            font=FONTS['default']
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)

        # Info label (center)
        self.info_label = ttk.Label(
            self.frame,
            text="",
            anchor=tk.CENTER,
            font=FONTS['small'],
            foreground=COLORS['info']
        )
        self.info_label.grid(row=0, column=1, padx=10, pady=2)

        # Counter label (right)
        self.counter_label = ttk.Label(
            self.frame,
            text="",
            anchor=tk.E,
            font=FONTS['small']
        )
        self.counter_label.grid(row=0, column=2, sticky=tk.E, padx=5, pady=2)

    def set_status(self, text: str, status_type: str = 'default'):
        """
        Set main status text with color

        Args:
            text: Status text
            status_type: Type of status for coloring
        """
        self.status_label.configure(text=text)
        set_status_color(self.status_label, status_type)

    def set_info(self, text: str):
        """Set info text in center"""
        self.info_label.configure(text=text)

    def set_counter(self, text: str):
        """Set counter text on right"""
        self.counter_label.configure(text=text)

    def clear_info(self):
        """Clear info label"""
        self.info_label.configure(text="")

    def clear_counter(self):
        """Clear counter label"""
        self.counter_label.configure(text="")

    def clear_all(self):
        """Clear all sections"""
        self.set_status("Ready", 'default')
        self.clear_info()
        self.clear_counter()


def show_context_menu(event, menu: tk.Menu):
    """
    Show context menu at mouse position

    Args:
        event: Mouse event
        menu: Menu to show
    """
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()


def confirm_dialog(parent, title: str, message: str) -> bool:
    """
    Show confirmation dialog

    Args:
        parent: Parent window
        title: Dialog title
        message: Dialog message

    Returns:
        True if user confirmed, False otherwise
    """
    from tkinter import messagebox
    return messagebox.askyesno(title, message, parent=parent)


def info_dialog(parent, title: str, message: str):
    """
    Show info dialog

    Args:
        parent: Parent window
        title: Dialog title
        message: Dialog message
    """
    from tkinter import messagebox
    messagebox.showinfo(title, message, parent=parent)


def error_dialog(parent, title: str, message: str):
    """
    Show error dialog

    Args:
        parent: Parent window
        title: Dialog title
        message: Dialog message
    """
    from tkinter import messagebox
    messagebox.showerror(title, message, parent=parent)


def warning_dialog(parent, title: str, message: str) -> bool:
    """
    Show warning dialog with OK/Cancel

    Args:
        parent: Parent window
        title: Dialog title
        message: Dialog message

    Returns:
        True if user clicked OK, False otherwise
    """
    from tkinter import messagebox
    return messagebox.askokcancel(title, message, parent=parent, icon='warning')
