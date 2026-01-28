"""CLI entry point for Workday Activity Logger."""

import argparse
import logging
import sys
from pathlib import Path

from activity_logger import ActivityLogger


def setup_logging(verbose: bool = False):
    """Setup logging configuration.
    
    Args:
        verbose: Enable debug logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Workday Activity Logger - Passive activity tracking optimized for AI summarization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main                     # Run with default config
  python -m src.main --verbose           # Run with debug logging
  python -m src.main --config my.json    # Use custom config file
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.json',
        help='Path to configuration file (default: config/config.json)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose debug logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Workday Activity Logger v2.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Print banner
    print("=" * 60)
    print("  Workday Activity Logger v2.0.0")
    print("  Passive activity tracking for AI summarization")
    print("=" * 60)
    print()
    
    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        logger.info("Using default configuration")
    
    try:
        # Initialize and start logger
        activity_logger = ActivityLogger(args.config)
        
        print(f"Configuration: {args.config}")
        print(f"Output directory: {activity_logger.config.output_directory}")
        print(f"Polling interval: {activity_logger.config.polling_interval}s")
        print(f"Idle timeout: {activity_logger.config.idle_timeout}s")
        print()
        print("Press Ctrl+C to stop...")
        print()
        
        # Start logging
        activity_logger.start()
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        logger.info("Activity Logger stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
