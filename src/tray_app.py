"""System tray application for Workday Activity Logger."""

import logging
import os
import threading

import pystray
from PIL import Image, ImageDraw

from .activity_logger import ActivityLogger
from .config_manager import PROJECT_ROOT

logger = logging.getLogger(__name__)


def _create_icon_image() -> Image.Image:
    """Generate a simple green circle icon."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size - 4, size - 4], fill="#4CAF50")
    return img


class TrayApp:
    """System tray application that manages ActivityLogger lifecycle."""

    def __init__(self, config_path: str = "config/config.json", verbose: bool = False):
        self.config_path = config_path
        self.verbose = verbose
        self.activity_logger = None
        self.logger_thread = None
        self.icon = None

    def _start_logging(self):
        """Start the activity logger in a background thread."""
        if self.logger_thread and self.logger_thread.is_alive():
            logger.info("Logger is already running")
            return

        self.activity_logger = ActivityLogger(self.config_path)
        self.logger_thread = threading.Thread(
            target=self.activity_logger.start, daemon=True
        )
        self.logger_thread.start()
        logger.info("Logger started")
        self._update_menu()

    def _stop_logging(self):
        """Stop the activity logger."""
        if self.activity_logger and self.activity_logger.running:
            self.activity_logger.stop()
            if self.logger_thread:
                self.logger_thread.join(timeout=5)
            logger.info("Logger stopped")
        self.activity_logger = None
        self.logger_thread = None
        self._update_menu()

    def _is_running(self) -> bool:
        return self.activity_logger is not None and self.activity_logger.running

    def _open_logs(self):
        """Open the logs folder in Explorer."""
        logs_dir = PROJECT_ROOT / "logs"
        logs_dir.mkdir(exist_ok=True)
        os.startfile(str(logs_dir))

    def _quit(self):
        """Stop logger and exit tray app."""
        self._stop_logging()
        if self.icon:
            self.icon.stop()

    def _build_menu(self) -> pystray.Menu:
        running = self._is_running()
        return pystray.Menu(
            pystray.MenuItem(
                "Stop Logging" if running else "Start Logging",
                lambda: self._stop_logging() if self._is_running() else self._start_logging(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Logs", lambda: self._open_logs()),
            pystray.MenuItem("Quit", lambda: self._quit()),
        )

    def _update_menu(self):
        if self.icon:
            self.icon.menu = self._build_menu()
            self.icon.update_menu()

    def run(self):
        """Launch the tray app. Blocks until quit."""
        self.icon = pystray.Icon(
            name="diary-ai",
            icon=_create_icon_image(),
            title="Workday Activity Logger",
            menu=self._build_menu(),
        )

        # Auto-start logging
        self.icon.visible = True
        self._start_logging()

        # Blocks on the main thread (required by pystray on Windows)
        self.icon.run()
