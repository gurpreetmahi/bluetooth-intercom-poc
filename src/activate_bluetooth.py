"""
Bluetooth Device Activation Helper
Helps activate Bluetooth devices before running the intercom test
"""

import pyaudio
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def play_test_tone(device_idx, device_name, duration=2):
    """
    Play a test tone to activate Bluetooth device
    
    Args:
        device_idx: Device index
        device_name: Device name for display
        duration: Duration in seconds
    """
    import numpy as np
    
    print(f"\n🔊 Playing test tone to activate: {device_name}")
    print(f"   You should hear a beep in the device...")
    
    p = pyaudio.PyAudio()
    
    try:
        # Generate a simple 440Hz sine wave (A note)
        sample_rate = 8000
        frequency = 440.0
        samples = int(sample_rate * duration)
        
        # Create sine wave
        t = np.linspace(0, duration, samples, False)
        tone = np.sin(frequency * 2 * np.pi * t)
        
        # Convert to 16-bit PCM
        tone = (tone * 32767).astype(np.int16)
        
        # Open output stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True,
            output_device_index=device_idx,
            frames_per_buffer=1024
        )
        
        # Play the tone
        stream.write(tone.tobytes())
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        
        print(f"✓ Test tone played successfully!")
        print(f"  Device should now be active for audio")
        return True
        
    except Exception as e:
        print(f"❌ Failed to activate device: {e}")
        return False
    finally:
        p.terminate()


def get_bluetooth_devices():
    """Get all Bluetooth headset devices"""
    import re
    
    p = pyaudio.PyAudio()
    bt_devices = {}
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        if 'Headset' in info['name'] and 'bthhfenum' in info['name']:
            matches = re.findall(r'\(([^)]+)\)', info['name'])
            if matches:
                device_name = matches[-1]
            else:
                device_name = info['name']
            
            if device_name not in bt_devices:
                bt_devices[device_name] = {}
            
            if info['maxInputChannels'] > 0:
                bt_devices[device_name]['input'] = i
            if info['maxOutputChannels'] > 0:
                bt_devices[device_name]['output'] = i
    
    p.terminate()
    return bt_devices


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("BLUETOOTH DEVICE ACTIVATION HELPER")
    print("="*60)
    print("\nThis tool helps activate your Bluetooth devices")
    print("by playing test tones through them.\n")
    
    # Get devices
    bt_devices = get_bluetooth_devices()
    
    if not bt_devices:
        print("❌ No Bluetooth devices found!")
        print("Make sure Bluetooth devices are paired with your PC")
        return
    
    print(f"Found {len(bt_devices)} Bluetooth device(s):\n")
    
    device_list = []
    for i, (name, info) in enumerate(bt_devices.items(), 1):
        has_output = 'output' in info
        print(f"  {i}. {name}")
        if has_output:
            print(f"     ✓ Speaker available")
            device_list.append((name, info))
        else:
            print(f"     ⚠️  No speaker detected")
    
    if not device_list:
        print("\n❌ No devices with speakers found!")
        return
    
    print("\n" + "="*60)
    print("ACTIVATION OPTIONS")
    print("="*60)
    print("\n1. Activate all devices")
    print("2. Activate specific device")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🔊 Activating all devices...")
        for name, info in device_list:
            if 'output' in info:
                play_test_tone(info['output'], name)
                time.sleep(1)
        
        print("\n" + "="*60)
        print("✅ All devices have been activated!")
        print("="*60)
        print("\nNow run the intercom test:")
        print("  python src\\bluetooth_intercom_test.py\n")
        
    elif choice == '2':
        print("\nSelect device to activate:")
        for i, (name, _) in enumerate(device_list, 1):
            print(f"  {i}. {name}")
        
        device_num = input(f"\nEnter device number (1-{len(device_list)}): ").strip()
        try:
            idx = int(device_num) - 1
            if 0 <= idx < len(device_list):
                name, info = device_list[idx]
                if 'output' in info:
                    play_test_tone(info['output'], name)
                    
                    print("\n✅ Device activated!")
                    print("\nWant to activate another? Run this script again")
                    print("or activate the second device manually through")
                    print("Windows Sound settings.\n")
            else:
                print("Invalid device number")
        except ValueError:
            print("Invalid input")
            
    elif choice == '3':
        print("Exiting...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
