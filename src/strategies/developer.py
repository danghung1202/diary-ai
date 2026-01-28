"""Developer tools strategy for window title extraction."""

import logging
from typing import Optional
from .base import ActivityStrategy, ActivityInfo

logger = logging.getLogger(__name__)


class DeveloperToolsStrategy(ActivityStrategy):
    """Strategy for developer tools (VS Code, Terminal, etc)."""

    def __init__(self, config_manager):
        """Initialize developer tools strategy.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.developer_tools = config_manager.developer_tools

    def can_handle(self, process_name: str) -> bool:
        """Check if this is a developer tool process."""
        return process_name.lower() in self.developer_tools

    def extract_activity(self, window_info) -> Optional[ActivityInfo]:
        """Extract activity from developer tool window.
        
        Args:
            window_info: WindowInfo object
            
        Returns:
            ActivityInfo with parsed title information
        """
        process_name = window_info.process_name
        window_title = window_info.window_title or "Untitled"
        
        # Parse title for specific tools
        description = self._parse_title(process_name, window_title)
        
        return ActivityInfo(
            app_name=self._get_friendly_name(process_name),
            description=description,
            activity_type="developer"
        )

    def _parse_title(self, process_name: str, title: str) -> str:
        """Parse window title to extract meaningful information.
        
        Args:
            process_name: Process name
            title: Window title
            
        Returns:
            Parsed description
        """
        process_lower = process_name.lower()
        
        # VS Code: Extract filename/folder
        if "code.exe" in process_lower:
            # Format: "filename.ext - FolderName - Visual Studio Code"
            if " - " in title:
                parts = title.split(" - ")
                if len(parts) >= 2:
                    filename = parts[0].strip()
                    # If it looks like a file path, use backticks
                    if "/" in filename or "\\" in filename or "." in filename:
                        return f"`{filename}`"
                    return filename
            return title
        
        # Terminal/PowerShell: Keep full title (often shows current command)
        elif any(x in process_lower for x in ["powershell", "terminal", "cmd"]):
            # Format might be: "PowerShell 7.x" or "Administrator: Windows PowerShell"
            # Or might show current directory/command
            if title:
                return f"`{title}`"
            return "Terminal"
        
        # Default: return title as-is
        return title

    def _get_friendly_name(self, process_name: str) -> str:
        """Get friendly display name for developer tool."""
        name_map = {
            "code.exe": "VS Code",
            "powershell.exe": "PowerShell",
            "windowsterminal.exe": "Terminal",
            "cmd.exe": "CMD",
            "pycharm64.exe": "PyCharm",
            "idea64.exe": "IntelliJ",
            "devenv.exe": "Visual Studio"
        }
        return name_map.get(process_name.lower(), process_name.replace(".exe", ""))
