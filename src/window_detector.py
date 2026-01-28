"""Window detection functionality for Windows."""

import logging
from typing import Optional, List, Dict
from dataclasses import dataclass

try:
    import win32gui
    import win32process
    import psutil
except ImportError:
    raise ImportError("Please install required packages: pip install pywin32 psutil")

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Information about a window."""
    process_name: str
    window_title: str
    pid: int
    hwnd: int


class WindowDetector:
    """Detects and extracts information from Windows windows."""

    def __init__(self, config_manager):
        """Initialize window detector.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager

    def get_foreground_window(self) -> Optional[WindowInfo]:
        """Get information about the currently active (foreground) window.
        
        Returns:
            WindowInfo object or None if unable to detect
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None

            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                logger.debug(f"Unable to get process name for PID {pid}")
                return None

            # Check blacklist
            if process_name.lower() in self.config.blacklist_processes:
                logger.debug(f"Process {process_name} is blacklisted")
                return None

            return WindowInfo(
                process_name=process_name,
                window_title=window_title,
                pid=pid,
                hwnd=hwnd
            )

        except Exception as e:
            logger.error(f"Error getting foreground window: {e}")
            return None

    def scan_background_windows(self) -> List[Dict[str, str]]:
        """Scan for meeting applications running in background.
        
        Returns:
            List of dictionaries containing meeting app info
        """
        meetings = []
        meeting_whitelist = self.config.meeting_whitelist

        try:
            # Enumerate all windows
            def enum_handler(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:  # Skip windows without title
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            process_name = process.name()
                            
                            # Check if it's a meeting app
                            if process_name.lower() in meeting_whitelist:
                                meetings.append({
                                    "app": process_name,
                                    "title": window_title
                                })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

            win32gui.EnumWindows(enum_handler, None)
            
            # Deduplicate by app name (keep first occurrence)
            seen = set()
            unique_meetings = []
            for meeting in meetings:
                if meeting["app"] not in seen:
                    seen.add(meeting["app"])
                    unique_meetings.append(meeting)

            return unique_meetings

        except Exception as e:
            logger.error(f"Error scanning background windows: {e}")
            return []
