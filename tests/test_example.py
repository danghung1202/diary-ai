"""Example test file for Workday Activity Logger.

This is a template showing how to test the components.
Run with: pytest tests/
"""

import unittest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_manager import ConfigManager
from deduplicator import ActivityDeduplicator
from privacy_filter import PrivacyFilter


class TestConfigManager(unittest.TestCase):
    """Test configuration manager."""

    def test_default_config(self):
        """Test that default config loads."""
        # Use non-existent path to force defaults
        config = ConfigManager("nonexistent.json")
        
        self.assertEqual(config.polling_interval, 30)
        self.assertEqual(config.idle_timeout, 300)
        self.assertEqual(config.output_directory, Path("logs"))

    def test_config_properties(self):
        """Test config property accessors."""
        config = ConfigManager("nonexistent.json")
        
        self.assertIsInstance(config.blacklist_processes, list)
        self.assertIsInstance(config.browser_processes, list)
        self.assertIsInstance(config.privacy_keywords, list)


class TestActivityDeduplicator(unittest.TestCase):
    """Test activity deduplication."""

    def setUp(self):
        """Set up test fixtures."""
        self.dedup = ActivityDeduplicator()

    def test_first_entry_logs(self):
        """Test that first entry is always logged."""
        state = {
            "foreground": "Chrome: Google",
            "background": None
        }
        
        self.assertTrue(self.dedup.should_log(state))

    def test_duplicate_not_logged(self):
        """Test that duplicate state is not logged."""
        state = {
            "foreground": "Chrome: Google",
            "background": None
        }
        
        # First call should log
        self.assertTrue(self.dedup.should_log(state))
        
        # Second call with same state should not log
        self.assertFalse(self.dedup.should_log(state))

    def test_changed_foreground_logs(self):
        """Test that changed foreground activity logs."""
        state1 = {
            "foreground": "Chrome: Google",
            "background": None
        }
        state2 = {
            "foreground": "VS Code: main.py",
            "background": None
        }
        
        self.assertTrue(self.dedup.should_log(state1))
        self.assertTrue(self.dedup.should_log(state2))

    def test_changed_background_logs(self):
        """Test that changed background context logs."""
        state1 = {
            "foreground": "Chrome: Google",
            "background": None
        }
        state2 = {
            "foreground": "Chrome: Google",
            "background": ("Teams: Meeting",)
        }
        
        self.assertTrue(self.dedup.should_log(state1))
        self.assertTrue(self.dedup.should_log(state2))

    def test_reset(self):
        """Test deduplicator reset."""
        state = {
            "foreground": "Chrome: Google",
            "background": None
        }
        
        self.assertTrue(self.dedup.should_log(state))
        self.assertFalse(self.dedup.should_log(state))
        
        # After reset, same state should log again
        self.dedup.reset()
        self.assertTrue(self.dedup.should_log(state))


class TestPrivacyFilter(unittest.TestCase):
    """Test privacy filtering."""

    def setUp(self):
        """Set up test fixtures."""
        config = ConfigManager("nonexistent.json")
        self.filter = PrivacyFilter(config)

    def test_clean_description_passes(self):
        """Test that clean description passes through."""
        desc = "Working on project documentation"
        result = self.filter.filter_description(desc)
        
        self.assertEqual(result, desc)

    def test_sensitive_keyword_redacted(self):
        """Test that sensitive keywords are redacted."""
        desc = "Resetting my password for the bank account"
        result = self.filter.filter_description(desc)
        
        self.assertEqual(result, "[REDACTED - Privacy]")

    def test_clean_url_passes(self):
        """Test that clean URL passes through."""
        url = "https://github.com/project/repo"
        result = self.filter.filter_url(url)
        
        self.assertEqual(result, url)

    def test_sensitive_url_redacted(self):
        """Test that URLs with sensitive patterns are redacted."""
        url = "https://example.com/reset?token=abc123"
        result = self.filter.filter_url(url)
        
        self.assertIn("REDACTED", result)


if __name__ == "__main__":
    unittest.main()
