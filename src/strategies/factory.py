"""Strategy factory for selecting appropriate activity extraction strategy."""

import logging
from typing import List
from .base import ActivityStrategy
from .browser import BrowserStrategy
from .developer import DeveloperToolsStrategy
from .generic import GenericStrategy

logger = logging.getLogger(__name__)


class StrategyFactory:
    """Factory for creating and selecting activity extraction strategies."""

    def __init__(self, config_manager):
        """Initialize strategy factory.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        
        # Initialize strategies in priority order
        # (Generic should always be last as it handles everything)
        self.strategies: List[ActivityStrategy] = [
            BrowserStrategy(config_manager),
            DeveloperToolsStrategy(config_manager),
            GenericStrategy()  # Fallback
        ]

    def get_strategy(self, process_name: str) -> ActivityStrategy:
        """Get appropriate strategy for the given process.
        
        Args:
            process_name: Name of the process
            
        Returns:
            Appropriate ActivityStrategy instance
        """
        for strategy in self.strategies:
            if strategy.can_handle(process_name):
                logger.debug(f"Selected {strategy.__class__.__name__} for {process_name}")
                return strategy
        
        # Should never reach here as GenericStrategy handles everything
        logger.warning(f"No strategy found for {process_name}, using Generic")
        return self.strategies[-1]
