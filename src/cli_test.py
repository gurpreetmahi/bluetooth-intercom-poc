"""
CLI Test Utility - Command-line interface for testing Bluetooth and audio
"""

import sys
import logging
from pathlib import Path
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from bluetooth_manager import BluetoothManager
from audio_router import AudioRouter


def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def test_bluetooth_discovery():
    """Test Bluetooth device discovery"""
    print("\n=== Testing Bluetooth Discovery ===")
    config = load_config()
    bt_manager = BluetoothManager(config)
    
    devices = bt_manager.discover_devices()
    
    if devices:
        print(f"\nFound {len(devices)} device(s):")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device.alias} - {device.address}")
    else:
        print("No devices found")
    
    return devices


def test_audio_devices():
    """Test audio device listing"""
    print("\n=== Testing Audio Devices ===")
    config = load_config()
    audio_router = AudioRouter(config)
    
    devices = audio_router.list_audio_devices()
    
    if devices:
        print(f"\nFound {len(devices)} audio device(s):")
        for device in devices:
            print(f"  [{device['index']}] {device['name']}")
            print(f"      Inputs: {device['input_channels']}, "
                  f"Outputs: {device['output_channels']}, "
                  f"Rate: {device['sample_rate']} Hz")
    else:
        print("No audio devices found")
    
    audio_router.cleanup()


def interactive_menu():
    """Interactive test menu"""
    print("\n" + "="*50)
    print("Bluetooth Intercom POC - CLI Test Utility")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Test Bluetooth device discovery")
        print("2. List audio devices")
        print("3. Run full test")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            test_bluetooth_discovery()
        elif choice == '2':
            test_audio_devices()
        elif choice == '3':
            test_bluetooth_discovery()
            test_audio_devices()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again")


def main():
    """Main CLI entry point"""
    setup_logging()
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
