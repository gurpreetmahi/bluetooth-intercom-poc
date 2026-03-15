"""
Bluetooth Intercom Test - Improved version with device activation
"""

import pyaudio
import threading
import time
import logging
import sys
import win32com.client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000  # HFP Bluetooth profile uses 8kHz


def get_bluetooth_devices(p):
    """Get all Bluetooth headset devices"""
    bt_devices = {}
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        # Look for Bluetooth headsets
        if 'Headset' in info['name'] and 'bthhfenum' in info['name']:
            # Extract device name from complex Windows naming
            import re
            matches = re.findall(r'\(([^)]+)\)', info['name'])
            if matches:
                device_name = matches[-1]
            else:
                device_name = info['name']
            
            if device_name not in bt_devices:
                bt_devices[device_name] = {}
            
            if info['maxInputChannels'] > 0:
                bt_devices[device_name]['input'] = i
                bt_devices[device_name]['input_info'] = info
            if info['maxOutputChannels'] > 0:
                bt_devices[device_name]['output'] = i
                bt_devices[device_name]['output_info'] = info
    
    return bt_devices


def test_device_availability(p, device_idx, is_input=True):
    """
    Test if a device can be opened
    
    Returns:
        True if device can be opened, False otherwise
    """
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=is_input,
            output=not is_input,
            input_device_index=device_idx if is_input else None,
            output_device_index=device_idx if not is_input else None,
            frames_per_buffer=CHUNK,
            start=False  # Don't start the stream yet
        )
        stream.close()
        return True
    except Exception as e:
        logger.debug(f"Device {device_idx} not available: {e}")
        return False


def activate_bluetooth_audio(device_name):
    """
    Attempt to activate Bluetooth audio for a device
    
    This is a placeholder - actual activation requires Windows APIs
    """
    logger.info(f"Attempting to activate: {device_name}")
    
    # TODO: Implement actual device activation using Windows Audio APIs
    # For now, we rely on manual activation
    
    print(f"\n⚠️  Please ensure '{device_name}' is actively playing audio")
    print(f"   Try: Settings -> Bluetooth -> {device_name} -> Connect")
    print(f"   Or play a sound/music through this device first")
    
    response = input(f"\nIs '{device_name}' now active and ready? (y/n): ").strip().lower()
    return response == 'y'


def bluetooth_intercom(p, device_a, device_b, duration=30):
    """
    Run Bluetooth intercom between two devices
    
    Args:
        p: PyAudio instance
        device_a: Device A configuration dict
        device_b: Device B configuration dict
        duration: Duration in seconds
    """
    logger.info("Setting up Bluetooth intercom...")
    
    try:
        # Open all streams
        logger.info("Opening Device A streams...")
        stream_a_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_a['input'],
            frames_per_buffer=CHUNK
        )
        
        stream_a_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=device_a['output'],
            frames_per_buffer=CHUNK
        )
        
        logger.info("Opening Device B streams...")
        stream_b_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_b['input'],
            frames_per_buffer=CHUNK
        )
        
        stream_b_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=device_b['output'],
            frames_per_buffer=CHUNK
        )
        
        logger.info("✓ All streams opened successfully!")
        
        print("\n" + "="*60)
        print("🎉 BLUETOOTH INTERCOM ACTIVE!")
        print("="*60)
        print(f"Device A: {device_a['name']}")
        print(f"Device B: {device_b['name']}")
        print(f"Duration: {duration}s (or press Ctrl+C to stop)")
        print("="*60)
        print("\n💬 Speak into either device - audio will be routed!")
        print()
        
        stop_event = threading.Event()
        packets_a_to_b = [0]  # Use list for mutable counter
        packets_b_to_a = [0]
        
        def route_a_to_b():
            """Route Device A mic to Device B speaker"""
            while not stop_event.is_set():
                try:
                    data = stream_a_in.read(CHUNK, exception_on_overflow=False)
                    stream_b_out.write(data)
                    packets_a_to_b[0] += 1
                except Exception as e:
                    if not stop_event.is_set():
                        logger.error(f"A->B routing error: {e}")
                        break
        
        def route_b_to_a():
            """Route Device B mic to Device A speaker"""
            while not stop_event.is_set():
                try:
                    data = stream_b_in.read(CHUNK, exception_on_overflow=False)
                    stream_a_out.write(data)
                    packets_b_to_a[0] += 1
                except Exception as e:
                    if not stop_event.is_set():
                        logger.error(f"B->A routing error: {e}")
                        break
        
        # Start routing threads
        thread_a_to_b = threading.Thread(target=route_a_to_b, daemon=True)
        thread_b_to_a = threading.Thread(target=route_b_to_a, daemon=True)
        
        thread_a_to_b.start()
        thread_b_to_a.start()
        
        # Run for specified duration
        try:
            for remaining in range(duration, 0, -1):
                print(f"\rTime: {remaining}s | A→B: {packets_a_to_b[0]} | B→A: {packets_b_to_a[0]} packets", 
                      end='', flush=True)
                time.sleep(1)
            print("\n")
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        
        # Stop routing
        stop_event.set()
        thread_a_to_b.join(timeout=2)
        thread_b_to_a.join(timeout=2)
        
        # Cleanup
        for stream in [stream_a_in, stream_a_out, stream_b_in, stream_b_out]:
            stream.stop_stream()
            stream.close()
        
        print("\n" + "="*60)
        logger.info("✓ Bluetooth intercom completed successfully!")
        logger.info(f"Total packets: A→B: {packets_a_to_b[0]}, B→A: {packets_b_to_a[0]}")
        print("="*60)
        return True
        
    except Exception as e:
        logger.error(f"❌ Bluetooth intercom failed: {e}", exc_info=True)
        print("\n" + "="*60)
        print("❌ FAILED TO START INTERCOM")
        print("="*60)
        print("\nPossible reasons:")
        print("1. Bluetooth devices not in active audio mode")
        print("2. Another application is using the devices")
        print("3. Devices disconnected during setup")
        print("\nTroubleshooting:")
        print("• Open Windows Sound settings")
        print("• Click on each Bluetooth device")
        print("• Test audio playback to ensure they're active")
        print("• Try again after confirming both devices work")
        print()
        return False


def main():
    """Main entry point"""
    p = pyaudio.PyAudio()
    
    try:
        print("\n" + "="*60)
        print("BLUETOOTH INTERCOM TEST")
        print("="*60)
        
        # Get Bluetooth devices
        bt_devices = get_bluetooth_devices(p)
        
        if not bt_devices:
            print("\n❌ No Bluetooth headsets found!")
            print("Make sure Bluetooth devices are paired with your PC")
            return False
        
        print(f"\nFound {len(bt_devices)} Bluetooth device(s):")
        complete_devices = []
        
        for i, (name, info) in enumerate(bt_devices.items(), 1):
            has_input = 'input' in info
            has_output = 'output' in info
            
            print(f"\n  {i}. {name}")
            if has_input:
                print(f"     ✓ Microphone (device {info['input']})")
            if has_output:
                print(f"     ✓ Speaker (device {info['output']})")
            
            if has_input and has_output:
                complete_devices.append((name, info))
                print(f"     ✅ Complete device")
            else:
                print(f"     ⚠️  Incomplete device")
        
        if len(complete_devices) < 2:
            print(f"\n❌ Need at least 2 complete Bluetooth devices!")
            print(f"Found: {len(complete_devices)}")
            return False
        
        print("\n" + "="*60)
        print("DEVICE SELECTION")
        print("="*60)
        
        # Auto-select first two devices
        device_a_name, device_a_info = complete_devices[0]
        device_b_name, device_b_info = complete_devices[1]
        
        print(f"\nDevice A (Person A): {device_a_name}")
        print(f"Device B (Person B): {device_b_name}")
        
        # Check availability
        print("\n" + "="*60)
        print("DEVICE AVAILABILITY CHECK")
        print("="*60)
        
        print(f"\nChecking {device_a_name}...")
        device_a_available = (
            test_device_availability(p, device_a_info['input'], is_input=True) and
            test_device_availability(p, device_a_info['output'], is_input=False)
        )
        
        if device_a_available:
            print(f"✓ {device_a_name} is available")
        else:
            print(f"⚠️  {device_a_name} is NOT available")
            if not activate_bluetooth_audio(device_a_name):
                return False
        
        print(f"\nChecking {device_b_name}...")
        device_b_available = (
            test_device_availability(p, device_b_info['input'], is_input=True) and
            test_device_availability(p, device_b_info['output'], is_input=False)
        )
        
        if device_b_available:
            print(f"✓ {device_b_name} is available")
        else:
            print(f"⚠️  {device_b_name} is NOT available")
            if not activate_bluetooth_audio(device_b_name):
                return False
        
        # Start intercom
        print("\n" + "="*60)
        print("STARTING INTERCOM")
        print("="*60)
        
        device_a_config = {
            'name': device_a_name,
            'input': device_a_info['input'],
            'output': device_a_info['output']
        }
        
        device_b_config = {
            'name': device_b_name,
            'input': device_b_info['input'],
            'output': device_b_info['output']
        }
        
        duration = 30  # Default 30 seconds
        
        print("\nPress Enter to start (or Ctrl+C to cancel)...")
        try:
            input()
        except KeyboardInterrupt:
            print("\nCancelled")
            return False
        
        return bluetooth_intercom(p, device_a_config, device_b_config, duration)
        
    finally:
        p.terminate()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
