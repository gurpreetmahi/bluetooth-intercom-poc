"""
Step-by-step Bluetooth Device Activation Guide
Walks user through activating devices one at a time
"""

import pyaudio
import time
import sys

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000


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
                bt_devices[device_name] = {'name': device_name}
            
            if info['maxInputChannels'] > 0:
                bt_devices[device_name]['input'] = i
            if info['maxOutputChannels'] > 0:
                bt_devices[device_name]['output'] = i
    
    p.terminate()
    return bt_devices


def test_device_active(device_idx, device_name):
    """Test if device can actually be opened"""
    p = pyaudio.PyAudio()
    
    print(f"\n🔍 Testing if '{device_name}' is active...")
    
    try:
        # Try to open output stream
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=device_idx,
            frames_per_buffer=CHUNK
        )
        stream.close()
        p.terminate()
        print(f"✅ SUCCESS! '{device_name}' is active and ready!")
        return True
    except Exception as e:
        p.terminate()
        print(f"❌ NOT ACTIVE: {e}")
        return False


def main():
    """Interactive activation guide"""
    print("\n" + "="*70)
    print("BLUETOOTH DEVICE ACTIVATION - STEP-BY-STEP GUIDE")
    print("="*70)
    
    # Get devices
    bt_devices = get_bluetooth_devices()
    
    if len(bt_devices) < 2:
        print("\n❌ Need at least 2 Bluetooth devices paired!")
        print(f"Currently found: {len(bt_devices)}")
        return 1
    
    print(f"\nFound {len(bt_devices)} Bluetooth device(s):\n")
    device_list = [(name, info) for name, info in bt_devices.items() 
                   if 'output' in info]
    
    for i, (name, _) in enumerate(device_list, 1):
        print(f"  {i}. {name}")
    
    if len(device_list) < 2:
        print("\n❌ Need at least 2 devices with speakers!")
        return 1
    
    print("\n" + "="*70)
    print("We'll activate the first 2 devices for the intercom")
    print("="*70)
    
    # Device A
    device_a_name = device_list[0][0]
    device_a_info = device_list[0][1]
    
    print(f"\n{'='*70}")
    print(f"STEP 1: ACTIVATE DEVICE A - '{device_a_name}'")
    print("="*70)
    print("\n📋 Follow these steps:")
    print("\n1. Press Windows key + I (or open Settings)")
    print("2. Go to: System → Sound")
    print("3. Scroll down to 'Output devices'")
    print(f"4. Find and click on: '{device_a_name}'")
    print("5. Look for the 'Test' button")
    print("6. Click 'Test' - you should hear a tone in the device")
    print("\n⚠️  IMPORTANT: Keep the Settings window OPEN!")
    
    input("\n▶️  Press Enter after you've clicked 'Test' and heard the tone...")
    
    # Test Device A
    if 'output' in device_a_info:
        if not test_device_active(device_a_info['output'], device_a_name):
            print("\n❌ Device A is not active yet!")
            print("\nTroubleshooting:")
            print("• Make sure you clicked 'Test' in Windows Sound settings")
            print("• The device should show 'Connected - Voice, music'")
            print("• Try disconnecting and reconnecting the device")
            print("\nRun this script again after fixing.")
            return 1
    
    # Device B
    device_b_name = device_list[1][0]
    device_b_info = device_list[1][1]
    
    print(f"\n{'='*70}")
    print(f"STEP 2: ACTIVATE DEVICE B - '{device_b_name}'")
    print("="*70)
    print("\n📋 In the SAME Settings window:")
    print(f"\n1. Scroll to find: '{device_b_name}'")
    print("2. Click on this device")
    print("3. Click 'Test' - you should hear a tone")
    print("\n⚠️  Keep Settings window open!")
    
    input("\n▶️  Press Enter after you've clicked 'Test' and heard the tone...")
    
    # Test Device B
    if 'output' in device_b_info:
        if not test_device_active(device_b_info['output'], device_b_name):
            print("\n❌ Device B is not active yet!")
            print("\nTroubleshooting:")
            print("• Make sure you clicked 'Test' in Windows Sound settings")
            print("• The device should show 'Connected - Voice, music'")
            print("\nRun this script again after fixing.")
            return 1
    
    # Both devices active!
    print("\n" + "="*70)
    print("✅ ✅ SUCCESS! BOTH DEVICES ARE ACTIVE! ✅ ✅")
    print("="*70)
    
    print(f"\n✓ Device A: {device_a_name}")
    print(f"✓ Device B: {device_b_name}")
    
    print("\n" + "="*70)
    print("FINAL STEP: RUN THE INTERCOM TEST")
    print("="*70)
    
    print("\n⚡ IMPORTANT: Do this IMMEDIATELY (within 10 seconds):")
    print("\n   python src\\bluetooth_intercom_test.py")
    
    print("\nOr press Enter here to launch it automatically...")
    
    try:
        response = input("\n▶️  Press Enter to launch intercom test (or Ctrl+C to exit): ")
        
        # Launch the test
        print("\n🚀 Launching Bluetooth intercom test...\n")
        import subprocess
        result = subprocess.run(
            ["python", "src\\bluetooth_intercom_test.py"],
            cwd="."
        )
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n\n📝 Manual launch instructions:")
        print("   1. Keep Settings window open")
        print("   2. Run: python src\\bluetooth_intercom_test.py")
        print("   3. When asked if devices are active, press 'y'\n")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
