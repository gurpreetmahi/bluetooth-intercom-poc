"""
Bluetooth Intercom POC - Main Application Entry Point
"""

import sys
import logging
from pathlib import Path
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from gui import IntercomGUI
from bluetooth_manager import BluetoothManager
from audio_router import AudioRouter


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def setup_logging(config):
    """Configure logging based on config"""
    log_level = getattr(logging, config['logging']['level'])
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = []
    
    if config['logging']['console']:
        handlers.append(logging.StreamHandler())
    
    if config['logging']['file']:
        log_file = Path(__file__).parent.parent / config['logging']['file']
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )


def main():
    """Main application entry point"""
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        logger.info("Starting Bluetooth Intercom POC")
        
        # Initialize components
        bluetooth_manager = BluetoothManager(config)
        audio_router = AudioRouter(config)
        
        # Start GUI
        app = IntercomGUI(config, bluetooth_manager, audio_router)
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
