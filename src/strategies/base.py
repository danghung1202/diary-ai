"""Base strategy interface for activity extraction."""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class ActivityInfo:
    """Information about an activity."""
    app_name: str
    description: str
    activity_type: str  # "browser", "developer", "generic"


class ActivityStrategy(ABC):
    """Abstract base class for activity extraction strategies."""

    @abstractmethod
    def can_handle(self, process_name: str) -> bool:
        """Check if this strategy can handle the given process.
        
        Args:
            process_name: Name of the process
            
        Returns:
            True if strategy can handle this process
        """
        pass

    @abstractmethod
    def extract_activity(self, window_info) -> Optional[ActivityInfo]:
        """Extract activity information from window.
        
        Args:
            window_info: WindowInfo object
            
        Returns:
            ActivityInfo object or None if extraction failed
        """
        pass
