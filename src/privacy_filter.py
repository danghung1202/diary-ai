"""Privacy filtering to protect sensitive information."""

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class PrivacyFilter:
    """Filters sensitive information from activity descriptions."""

    def __init__(self, config_manager):
        """Initialize privacy filter.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.privacy_keywords = config_manager.privacy_keywords

    def filter_description(self, description: str) -> Optional[str]:
        """Filter description for privacy concerns.
        
        Args:
            description: Activity description to filter
            
        Returns:
            Filtered description or None if should be completely redacted
        """
        if not description:
            return description

        description_lower = description.lower()

        # Check for privacy keywords
        for keyword in self.privacy_keywords:
            if keyword in description_lower:
                logger.info(f"Privacy keyword '{keyword}' detected, redacting")
                return "[REDACTED - Privacy]"

        return description

    def filter_url(self, url: str) -> Optional[str]:
        """Filter URL for privacy concerns.
        
        Args:
            url: URL to filter
            
        Returns:
            Filtered URL or redacted placeholder
        """
        if not url:
            return url

        url_lower = url.lower()

        # Check for privacy keywords in URL
        for keyword in self.privacy_keywords:
            if keyword in url_lower:
                logger.info(f"Privacy keyword '{keyword}' detected in URL, redacting")
                return "[REDACTED - Privacy]"

        # Check for common sensitive patterns
        sensitive_patterns = [
            "reset",
            "token=",
            "auth=",
            "key=",
            "secret=",
            "api_key=",
            "access_token=",
        ]

        for pattern in sensitive_patterns:
            if pattern in url_lower:
                logger.info(f"Sensitive pattern '{pattern}' detected in URL, redacting")
                return "[REDACTED - Sensitive URL]"

        return url

    def should_skip_entry(self, description: str) -> bool:
        """Determine if entire entry should be skipped.
        
        Args:
            description: Activity description
            
        Returns:
            True if entry should be skipped entirely
        """
        # Could implement stricter rules here if needed
        # For now, we redact rather than skip
        return False
