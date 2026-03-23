"""Configuration management for the Activity Logger."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ConfigManager:
    """Manages application configuration from JSON file."""

    DEFAULT_CONFIG = {
        "polling_interval_seconds": 30,
        "idle_timeout_seconds": 300,
        "output_directory": "logs",
        "blacklist_processes": [],
        "meeting_whitelist": ["Teams.exe", "Zoom.exe"],
        "privacy_keywords": ["password", "bank"],
        "browser_processes": ["chrome.exe", "msedge.exe"],
        "developer_tools": ["Code.exe", "powershell.exe"],
        "browser_url_timeout_seconds": 0.5
    }

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration JSON file
        """
        path = Path(config_path)
        self.config_path = path if path.is_absolute() else PROJECT_ROOT / path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults.
        
        Returns:
            Dictionary containing configuration values
        """
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}, using defaults")
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Merge with defaults
            config = self.DEFAULT_CONFIG.copy()
            config.update(user_config)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return self.DEFAULT_CONFIG.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    @property
    def polling_interval(self) -> int:
        """Get polling interval in seconds."""
        return self.config["polling_interval_seconds"]

    @property
    def idle_timeout(self) -> int:
        """Get idle timeout in seconds."""
        return self.config["idle_timeout_seconds"]

    @property
    def output_directory(self) -> Path:
        """Get output directory path."""
        path = Path(self.config["output_directory"])
        return path if path.is_absolute() else PROJECT_ROOT / path

    @property
    def blacklist_processes(self) -> List[str]:
        """Get list of blacklisted process names."""
        return [p.lower() for p in self.config["blacklist_processes"]]

    @property
    def meeting_whitelist(self) -> List[str]:
        """Get list of meeting app process names."""
        return [p.lower() for p in self.config["meeting_whitelist"]]

    @property
    def privacy_keywords(self) -> List[str]:
        """Get list of privacy-sensitive keywords."""
        return [k.lower() for k in self.config["privacy_keywords"]]

    @property
    def browser_processes(self) -> List[str]:
        """Get list of browser process names."""
        return [p.lower() for p in self.config["browser_processes"]]

    @property
    def developer_tools(self) -> List[str]:
        """Get list of developer tool process names."""
        return [p.lower() for p in self.config["developer_tools"]]

    @property
    def browser_url_timeout(self) -> float:
        """Get browser URL extraction timeout."""
        return self.config["browser_url_timeout_seconds"]
