"""Activity deduplication to reduce log bloat."""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ActivityDeduplicator:
    """Deduplicates activity entries to avoid logging redundant information."""

    def __init__(self):
        """Initialize deduplicator."""
        self.last_state: Optional[Dict[str, Any]] = None

    def should_log(self, current_state: Dict[str, Any]) -> bool:
        """Determine if current state should be logged.
        
        Only logs if:
        - This is the first entry, OR
        - Foreground activity has changed, OR
        - Background context has changed
        
        Args:
            current_state: Dictionary with 'foreground' and 'background' keys
            
        Returns:
            True if state should be logged
        """
        # First entry
        if self.last_state is None:
            self.last_state = current_state.copy()
            return True

        # Check if anything changed
        foreground_changed = (
            current_state.get("foreground") != self.last_state.get("foreground")
        )
        background_changed = (
            current_state.get("background") != self.last_state.get("background")
        )

        if foreground_changed or background_changed:
            logger.debug(
                f"State changed - Foreground: {foreground_changed}, "
                f"Background: {background_changed}"
            )
            self.last_state = current_state.copy()
            return True

        logger.debug("State unchanged, skipping log entry")
        return False

    def reset(self):
        """Reset deduplication state."""
        self.last_state = None
        logger.debug("Deduplicator reset")
