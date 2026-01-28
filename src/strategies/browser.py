"""Browser strategy for deep URL inspection."""

import logging
from typing import Optional
from .base import ActivityStrategy, ActivityInfo

try:
    import uiautomation as auto
except ImportError:
    auto = None
    logging.warning("uiautomation not installed, browser URL extraction will be limited")

logger = logging.getLogger(__name__)


class BrowserStrategy(ActivityStrategy):
    """Strategy for extracting URLs from browser windows using UI Automation."""

    def __init__(self, config_manager):
        """Initialize browser strategy.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.browser_processes = config_manager.browser_processes
        self.timeout = config_manager.browser_url_timeout
        self._handle_cache = {}

    def can_handle(self, process_name: str) -> bool:
        """Check if this is a browser process."""
        return process_name.lower() in self.browser_processes

    def extract_activity(self, window_info) -> Optional[ActivityInfo]:
        """Extract URL and title from browser window.
        
        Args:
            window_info: WindowInfo object
            
        Returns:
            ActivityInfo with URL or None if extraction failed
        """
        process_name = window_info.process_name
        
        # Try to extract URL using UI Automation
        url = self._extract_url_with_timeout(window_info)
        
        if url:
            description = f"[{url}]"
            if window_info.window_title:
                # Include page title if available
                description = f"{window_info.window_title} - [{url}]"
        else:
            # Fallback to window title only
            description = window_info.window_title or "Unknown page"
        
        return ActivityInfo(
            app_name=self._get_friendly_name(process_name),
            description=description,
            activity_type="browser"
        )

    def _extract_url_with_timeout(self, window_info) -> Optional[str]:
        """Extract URL from browser with timeout protection.
        
        Args:
            window_info: WindowInfo object
            
        Returns:
            URL string or None if extraction failed/timed out
        """
        if auto is None:
            logger.debug("UI Automation not available")
            return None

        try:
            # Set global timeout
            auto.SetGlobalSearchTimeout(self.timeout)
            
            # Get the window control
            window = auto.ControlFromHandle(window_info.hwnd)
            if not window:
                logger.debug("Could not get window control from handle")
                return None

            logger.debug(f"Attempting URL extraction for {window_info.process_name}")

            # Try to find address bar (different methods for different browsers)
            url = self._find_address_bar_chrome_edge(window)
            if url:
                logger.info(f"Successfully extracted URL: {url[:80]}...")
                return url
                
            if not url:
                url = self._find_address_bar_firefox(window)
                if url:
                    logger.info(f"Successfully extracted URL: {url[:80]}...")
                    return url
            
            logger.debug("All URL extraction methods failed, falling back to window title")
            return None

        except Exception as e:
            logger.debug(f"URL extraction failed: {e}")
            return None

    def _find_address_bar_chrome_edge(self, window) -> Optional[str]:
        """Find address bar in Chrome/Edge."""
        try:
            # Method 1: Search by Name "Address and search bar" (Chrome/Edge)
            edit_control = window.EditControl(
                Name="Address and search bar",
                searchDepth=10
            )
            
            if edit_control and edit_control.Exists(0, 0):
                url = edit_control.GetValuePattern().Value
                if url and (url.startswith(('http://', 'https://', 'file://')) or '.' in url):
                    logger.debug(f"Found URL via Name 'Address and search bar': {url[:50]}...")
                    return url
            
            # Method 2: Try Name "Search or enter web address" (Edge alternative)
            edit_control = window.EditControl(
                Name="Search or enter web address",
                searchDepth=10
            )
            
            if edit_control and edit_control.Exists(0, 0):
                url = edit_control.GetValuePattern().Value
                if url and (url.startswith(('http://', 'https://', 'file://')) or '.' in url):
                    logger.debug(f"Found URL via Name 'Search or enter web address': {url[:50]}...")
                    return url
            
            # Method 3: Try AutomationId for Chrome
            edit_control = window.EditControl(
                AutomationId="Chrome_OmniboxView",
                searchDepth=10
            )
            
            if edit_control and edit_control.Exists(0, 0):
                url = edit_control.GetValuePattern().Value
                if url and (url.startswith(('http://', 'https://', 'file://')) or '.' in url):
                    logger.debug(f"Found URL via AutomationId: {url[:50]}...")
                    return url
                    
        except Exception as e:
            logger.debug(f"Chrome/Edge address bar search failed: {e}")
        
        return None

    def _find_address_bar_firefox(self, window) -> Optional[str]:
        """Find address bar in Firefox."""
        try:
            # Firefox might use different control structure
            toolbar = window.ToolBarControl(searchDepth=5)
            if toolbar:
                edit_control = toolbar.EditControl()
                if edit_control and edit_control.Exists(0, 0):
                    url = edit_control.GetValuePattern().Value
                    if url and url.startswith(('http://', 'https://', 'file://', 'about:')):
                        return url
        except Exception as e:
            logger.debug(f"Firefox address bar search failed: {e}")
        
        return None

    def _get_friendly_name(self, process_name: str) -> str:
        """Get friendly display name for browser."""
        name_map = {
            "chrome.exe": "Chrome",
            "msedge.exe": "Edge",
            "firefox.exe": "Firefox",
            "brave.exe": "Brave",
            "opera.exe": "Opera"
        }
        return name_map.get(process_name.lower(), process_name.replace(".exe", ""))
