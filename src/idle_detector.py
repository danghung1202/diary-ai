"""Idle detection using keyboard and mouse activity monitoring."""

import logging
import time
from typing import Optional

try:
    from pynput import mouse, keyboard
except ImportError:
    raise ImportError("Please install pynput: pip install pynput")

logger = logging.getLogger(__name__)


class IdleDetector:
    """Detects user idle time based on keyboard and mouse activity."""

    def __init__(self, config_manager):
        """Initialize idle detector.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.idle_timeout = config_manager.idle_timeout
        self.last_activity_time = time.time()
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._running = False

    def start(self):
        """Start monitoring keyboard and mouse activity."""
        if self._running:
            logger.warning("IdleDetector already running")
            return

        self.last_activity_time = time.time()
        
        # Start mouse listener
        self._mouse_listener = mouse.Listener(
            on_move=self._on_activity,
            on_click=self._on_activity,
            on_scroll=self._on_activity
        )
        self._mouse_listener.start()

        # Start keyboard listener
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_activity
        )
        self._keyboard_listener.start()

        self._running = True
        logger.info("IdleDetector started")

    def stop(self):
        """Stop monitoring activity."""
        if not self._running:
            return

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        self._running = False
        logger.info("IdleDetector stopped")

    def _on_activity(self, *args, **kwargs):
        """Callback for any keyboard or mouse activity."""
        self.last_activity_time = time.time()

    def is_idle(self) -> bool:
        """Check if user is currently idle.
        
        Returns:
            True if idle time exceeds threshold
        """
        idle_duration = time.time() - self.last_activity_time
        return idle_duration > self.idle_timeout

    def get_idle_duration(self) -> float:
        """Get current idle duration in seconds.
        
        Returns:
            Idle duration in seconds
        """
        return time.time() - self.last_activity_time

    def reset(self):
        """Reset idle timer (mark activity now)."""
        self.last_activity_time = time.time()
