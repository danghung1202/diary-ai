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

    def scan_background_windows(self, exclude_hwnd=None) -> List[Dict[str, str]]:
        """Scan for meeting applications running in background.
        
        Args:
            exclude_hwnd: Window handle to exclude (usually the foreground window)
        
        Returns:
            List of dictionaries containing meeting app info
        """
        meetings = []
        meeting_whitelist = self.config.meeting_whitelist

        try:
            # Enumerate all windows
            def enum_handler(hwnd, ctx):
                # Skip the foreground window to avoid duplicate logging
                if exclude_hwnd and hwnd == exclude_hwnd:
                    logger.debug(f"Skipping foreground window (hwnd={hwnd})")
                    return
                    
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:  # Skip windows without title
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            process_name = process.name()
                            
                            # Check if it's a meeting app
                            if process_name.lower() in meeting_whitelist:
                                # Only include if it's actually a meeting (not just chat)
                                if self._is_meeting_window(process_name, window_title):
                                    meetings.append({
                                        "app": process_name,
                                        "title": window_title
                                    })
                                    logger.debug(f"Found background meeting: {process_name} - {window_title[:50]}")
                                else:
                                    logger.debug(f"Skipped non-meeting window: {window_title[:50]}")
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

    def _is_meeting_window(self, process_name: str, window_title: str) -> bool:
        """Check if a window is actually a meeting (not just chat).
        
        Args:
            process_name: Name of the process
            window_title: Title of the window
            
        Returns:
            True if this is a meeting window
        """
        process_lower = process_name.lower()
        title_lower = window_title.lower()
        
        # Teams-specific detection
        if "teams" in process_lower or "ms-teams" in process_lower:
            # Meeting indicators in Teams
            
            # meeting_keywords = [
            #     "meeting",           # "Meeting compact view"
            #     "call",              # "Call with John"
            #     "| calling",         # During a call
            #     "| in a call",       # In a call
            #     "in a meeting",      # In a meeting
            # ]
            
            # # Check if title contains meeting keywords
            # for keyword in meeting_keywords:
            #     if keyword in title_lower:
            #         logger.debug(f"Detected Teams meeting via keyword '{keyword}'")
            #         return True
            
            # Exclude chat windows explicitly
            if title_lower.startswith("chat |"):
                logger.debug("Excluded Teams chat window")
                return False
            else:    
                logger.debug(f"Detected Teams meeting because it's not a chat window: '{title_lower}'")
                return True    
        # Zoom-specific detection
        elif "zoom" in process_lower:
            # Zoom meeting window usually has "Zoom Meeting" in title
            if "zoom meeting" in title_lower:
                logger.debug("Detected Zoom meeting")
                return True
        
        # Google Meet (browser-based)
        elif "meet.google.com" in process_lower:
            logger.debug("Detected Google Meet")
            return True
        
        # Default: if it's in whitelist but no specific detection, don't log
        # This prevents false positives
        logger.debug(f"No meeting indicators found for {process_name}")
        return False
