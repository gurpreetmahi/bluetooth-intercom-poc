"""
Activate Bluetooth devices and hold streams open
This keeps devices active so the intercom can use them
"""

import pyaudio
import time
import sys
import re


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000


def get_bluetooth_devices():
    """Get all Bluetooth headset devices"""
    p = pyaudio.PyAudio()
    bt_devices = []
    
    print("\n🔍 Scanning audio devices...\n")
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        # Look for Bluetooth HFP devices
        if 'Headset' in info['name'] and 'bthhfenum' in info['name']:
            # Extract friendly name from parentheses
            matches = re.findall(r'\(([^)]+)\)', info['name'])
            if matches:
                friendly_name = matches[-1]
            else:
                friendly_name = info['name']
            
            device_entry = {
                'friendly_name': friendly_name,
                'full_name': info['name'],
                'index': i,
                'input_ch': info['maxInputChannels'],
                'output_ch': info['maxOutputChannels']
            }
            
            bt_devices.append(device_entry)
            print(f"  Found: {friendly_name}")
            print(f"    Input channels: {info['maxInputChannels']}")
            print(f"    Output channels: {info['maxOutputChannels']}")
            print()
    
    p.terminate()
    return bt_devices


def open_and_test_device(p, device):
    """Open audio stream on device and test it"""
    print(f"\n📡 Opening audio stream for: {device['friendly_name']}")
    
    try:
        # Open output stream
        if device['output_ch'] > 0:
            stream_out = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                output_device_index=device['index'],
                frames_per_buffer=CHUNK
            )
            print(f"  ✓ Output stream opened")
            
            # Play a brief tone
            import numpy as np
            frequency = 440  # Hz
            duration = 0.5  # seconds
            samples = int(RATE * duration)
            t = np.linspace(0, duration, samples, False)
            tone = np.sin(frequency * 2 * np.pi * t)
            audio_data = (tone * 32767 * 0.3).astype(np.int16).tobytes()
            
            stream_out.write(audio_data)
            print(f"  ✓ Test tone played")
            
            return stream_out
        else:
            print(f"  ⚠️  No output channels available")
            return None
            
    except Exception as e:
        print(f"  ❌ Failed to open: {e}")
        return None


def main():
    """Activate devices and hold streams"""
    print("\n" + "="*70)
    print("BLUETOOTH DEVICE ACTIVATION - STREAM HOLDER")
    print("="*70)
    print("\nThis script will:")
    print("  1. Find your Bluetooth devices")
    print("  2. Open audio streams to activate them")
    print("  3. Play test tones so you can hear them")
    print("  4. Keep streams open so you can run the intercom test")
    print("="*70)
    
    # Get devices
    devices = get_bluetooth_devices()
    
    if len(devices) < 2:
        print(f"\n❌ Need at least 2 Bluetooth devices!")
        print(f"   Currently found: {len(devices)}")
        print("\n💡 Make sure devices are:")
        print("   • Paired with your PC")
        print("   • Turned on")
        print("   • In Bluetooth range")
        return 1
    
    print(f"\n✅ Found {len(devices)} Bluetooth device(s)")
    
    # Filter devices with output capability
    output_devices = [d for d in devices if d['output_ch'] > 0]
    
    if len(output_devices) < 2:
        print(f"\n❌ Need at least 2 devices with output capability!")
        print(f"   Currently found: {len(output_devices)}")
        return 1
    
    # Use first 2 devices
    device_a = output_devices[0]
    device_b = output_devices[1]
    
    print("\n" + "="*70)
    print("SELECTED DEVICES:")
    print("="*70)
    print(f"\n  Device A: {device_a['friendly_name']}")
    print(f"  Device B: {device_b['friendly_name']}")
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    streams = []
    
    print("\n" + "="*70)
    print("ACTIVATING DEVICES...")
    print("="*70)
    
    # Open Device A
    stream_a = open_and_test_device(p, device_a)
    if stream_a:
        streams.append(stream_a)
        print(f"✅ Device A is ACTIVE")
    else:
        print(f"❌ Could not activate Device A")
        print("\n💡 Try this:")
        print("   1. Open Settings → System → Sound")
        print(f"   2. Find '{device_a['friendly_name']}'")
        print("   3. Click 'Test' to wake it up")
        print("   4. Run this script again IMMEDIATELY")
        p.terminate()
        return 1
    
    time.sleep(0.5)
    
    # Open Device B  
    stream_b = open_and_test_device(p, device_b)
    if stream_b:
        streams.append(stream_b)
        print(f"✅ Device B is ACTIVE")
    else:
        print(f"❌ Could not activate Device B")
        print("\n💡 Try this:")
        print("   1. Open Settings → System → Sound")
        print(f"   2. Find '{device_b['friendly_name']}'")
        print("   3. Click 'Test' to wake it up")
        print("   4. Run this script again IMMEDIATELY")
        for s in streams:
            s.close()
        p.terminate()
        return 1
    
    print("\n" + "="*70)
    print("✅ ✅ BOTH DEVICES ACTIVATED! ✅ ✅")
    print("="*70)
    
    print("\n🎉 Success! Both audio streams are now open and active.")
    print("\n⚡ NEXT STEP:")
    print("\n   Open a NEW terminal window and run:")
    print("\n      python src\\bluetooth_intercom_test.py")
    print("\n   (Keep THIS window open while running the test!)")
    
    print("\n" + "="*70)
    print("\nHolding streams open... Press Ctrl+C when done.\n")
    
    try:
        # Keep streams alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Closing streams...")
        for stream in streams:
            stream.close()
        p.terminate()
        print("✅ Done!\n")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
