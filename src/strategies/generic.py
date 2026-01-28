"""Generic fallback strategy for all other applications."""

import logging
from typing import Optional
from .base import ActivityStrategy, ActivityInfo

logger = logging.getLogger(__name__)


class GenericStrategy(ActivityStrategy):
    """Generic fallback strategy for any application."""

    def can_handle(self, process_name: str) -> bool:
        """This strategy handles all processes as fallback."""
        return True

    def extract_activity(self, window_info) -> Optional[ActivityInfo]:
        """Extract basic activity information from any window.
        
        Args:
            window_info: WindowInfo object
            
        Returns:
            ActivityInfo with process name and title
        """
        process_name = window_info.process_name
        window_title = window_info.window_title or "Untitled"
        
        return ActivityInfo(
            app_name=self._get_friendly_name(process_name),
            description=window_title,
            activity_type="generic"
        )

    def _get_friendly_name(self, process_name: str) -> str:
        """Get friendly display name for application.
        
        Args:
            process_name: Process executable name
            
        Returns:
            Friendly name
        """
        # Remove .exe extension
        name = process_name.replace(".exe", "").replace(".EXE", "")
        
        # Common application name mappings
        name_map = {
            "outlook": "Outlook",
            "winword": "Word",
            "excel": "Excel",
            "powerpnt": "PowerPoint",
            "notepad": "Notepad",
            "explorer": "Explorer",
            "mspaint": "Paint",
            "teams": "Teams",
            "slack": "Slack",
            "discord": "Discord",
            "spotify": "Spotify"
        }
        
        name_lower = name.lower()
        if name_lower in name_map:
            return name_map[name_lower]
        
        # Capitalize first letter
        return name.capitalize()
