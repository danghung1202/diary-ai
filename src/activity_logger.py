"""Main activity logger polling loop."""

import logging
import time
from datetime import datetime
from typing import Optional

from .config_manager import ConfigManager
from .window_detector import WindowDetector
from .strategies.factory import StrategyFactory
from .idle_detector import IdleDetector
from .deduplicator import ActivityDeduplicator
from .privacy_filter import PrivacyFilter
from .markdown_writer import MarkdownWriter

logger = logging.getLogger(__name__)


class ActivityLogger:
    """Main activity logger that coordinates all components."""

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize activity logger.
        
        Args:
            config_path: Path to configuration file
        """
        logger.info("Initializing Activity Logger...")
        
        # Initialize components
        self.config = ConfigManager(config_path)
        self.window_detector = WindowDetector(self.config)
        self.strategy_factory = StrategyFactory(self.config)
        self.idle_detector = IdleDetector(self.config)
        self.deduplicator = ActivityDeduplicator()
        self.privacy_filter = PrivacyFilter(self.config)
        self.markdown_writer = MarkdownWriter(self.config)
        
        self.running = False
        self.last_idle_state = False

    def start(self):
        """Start the activity logger."""
        logger.info("Starting Activity Logger...")
        logger.info(f"Polling interval: {self.config.polling_interval}s")
        logger.info(f"Idle timeout: {self.config.idle_timeout}s")
        logger.info(f"Output directory: {self.config.output_directory}")
        
        # Start idle detector
        self.idle_detector.start()
        
        self.running = True
        self._run_polling_loop()

    def stop(self):
        """Stop the activity logger."""
        logger.info("Stopping Activity Logger...")
        self.running = False
        self.idle_detector.stop()

    def _run_polling_loop(self):
        """Main polling loop."""
        logger.info("Polling loop started")
        
        try:
            while self.running:
                self._poll_activity()
                time.sleep(self.config.polling_interval)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()
        except Exception as e:
            logger.error(f"Error in polling loop: {e}", exc_info=True)
            self.stop()

    def _poll_activity(self):
        """Poll current activity and log if needed."""
        timestamp = datetime.now()
        
        # Step 1: Check idle state
        if self.idle_detector.is_idle():
            # Only log idle once when transitioning to idle
            if not self.last_idle_state:
                logger.info("User is idle")
                self.markdown_writer.write_idle_entry(timestamp)
                self.last_idle_state = True
                self.deduplicator.reset()
            return
        else:
            # User is active
            if self.last_idle_state:
                logger.info("User is active again")
                self.last_idle_state = False
                self.deduplicator.reset()

        # Step 2: Get foreground window
        window_info = self.window_detector.get_foreground_window()
        if not window_info:
            logger.debug("No foreground window detected")
            return

        logger.debug(
            f"Foreground: {window_info.process_name} - {window_info.window_title}"
        )

        # Step 3: Execute strategy to extract activity
        strategy = self.strategy_factory.get_strategy(window_info.process_name)
        activity_info = strategy.extract_activity(window_info)
        
        if not activity_info:
            logger.debug("No activity info extracted")
            return

        # Step 4: Apply privacy filter
        filtered_description = self.privacy_filter.filter_description(
            activity_info.description
        )
        if not filtered_description:
            logger.debug("Activity filtered out for privacy")
            return

        # Format foreground description
        foreground_description = f"**{activity_info.app_name}**: {filtered_description}"

        # Step 5: Scan background for meetings
        background_meetings = self.window_detector.scan_background_windows()
        background_context = []
        
        for meeting in background_meetings:
            app_name = meeting["app"].replace(".exe", "").capitalize()
            title = self.privacy_filter.filter_description(meeting["title"])
            if title:
                background_context.append(f"**{app_name}**: \"{title}\"")

        # Step 6: Check deduplication
        current_state = {
            "foreground": foreground_description,
            "background": tuple(background_context) if background_context else None
        }

        if not self.deduplicator.should_log(current_state):
            return

        # Step 7: Write to log
        logger.info(f"Logging: {activity_info.app_name}")
        self.markdown_writer.write_entry(
            timestamp=timestamp,
            foreground_description=foreground_description,
            background_context=background_context if background_context else None
        )
