"""
GUI package for Scrapey application.

This package contains all the GUI-related modules for the Scrapey application,
including the main window, preferences dialog, and preview window.
"""

from .main_window import MainWindow
from .preferences import open_preferences
from .preview import open_preview

__all__ = ['MainWindow', 'open_preferences', 'open_preview'] 