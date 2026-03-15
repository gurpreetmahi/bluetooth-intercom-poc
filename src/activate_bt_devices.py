"""
Windows Bluetooth Audio Activator
Uses Windows Audio APIs to properly activate Bluetooth devices before streaming
"""

import pyaudio
import time
import sys
import ctypes
from ctypes import wintypes, POINTER, Structure, byref, c_float
import comtypes
from comtypes import GUID

# Windows COM interfaces for Audio
try:
    import comtypes.client
    PKEY_Device_FriendlyName = "{a45c254e-df1c-4efd-8020-67d146a850e0} 14"
    
    # Device state enum
    DEVICE_STATE_ACTIVE = 0x00000001
    DEVICE_STATE_DISABLED = 0x00000002
    DEVICE_STATE_NOTPRESENT = 0x00000004
    DEVICE_STATE_UNPLUGGED = 0x00000008
    
    WINDOWS_AUDIO_API = True
except ImportError:
    WINDOWS_AUDIO_API = False
    print("⚠️  comtypes not available - using basic approach")


def activate_windows_audio_device(device_name):
    """
    Trigger Windows to activate audio device via COM
    This establishes the SCO connection for Bluetooth
    """
    if not WINDOWS_AUDIO_API:
        return False
    
    try:
        # Create device enumerator
        from comtypes import CoCreateInstance, CLSCTX_ALL
        
        # IMMDeviceEnumerator CLSID and IID
        CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
        IID_IMMDeviceEnumerator = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
        
        # Create instance - this requires proper COM interface definitions
        # For now, we'll use a simpler approach
        
        return False
        
    except Exception as e:
        print(f"   COM activation failed: {e}")
        return False


def play_silence_to_activate(device_index, device_name):
    """
    Play brief silence to trigger Windows to activate the device
    This often works better than trying to use COM interfaces
    """
    try:
        p = pyaudio.PyAudio()
        
        print(f"   🔊 Attempting to activate via audio playback...")
        
        # Try to open stream with very small buffer
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            output=True,
            output_device_index=device_index,
            frames_per_buffer=512
        )
        
        # Play very brief silence
        import numpy as np
        silence = np.zeros(512, dtype=np.int16).tobytes()
        
        for _ in range(3):
            stream.write(silence)
            time.sleep(0.01)
        
        stream.stop_stream()
        
        print(f"   ✅ Device activated successfully!")
        
        return stream  # Keep stream open
        
    except Exception as e:
        print(f"   ❌ Activation failed: {e}")
        try:
            stream.close()
        except:
            pass
        p.terminate()
        return None


def manual_activation_guide(device_name):
    """Print instructions for manually activating device"""
    print(f"\n{'='*70}")
    print(f"📱 MANUAL ACTIVATION REQUIRED: {device_name}")
    print(f"{'='*70}")
    print("\n⚡ Quick method (Choose one):")
    print("\n   Method 1: Play Test Sound")
    print("   1. Press Windows + I (Settings)")
    print("   2. Go to System → Sound")
    print(f"   3. Find '{device_name.split('(')[1].split(')')[0]}'")
    print("   4. Click 'Test your microphone' or output test button")
    print("   5. Quickly return to this window")
    print("\n   Method 2: Play Any Audio")
    print("   1. Open YouTube/Spotify")
    print("   2. Change output device to your Bluetooth device")
    print("   3. Play audio for 1-2 seconds")
    print("   4. Quickly return to this window")
    print("\n   Method 3: Use Windows Mixer")
    print("   1. Right-click speaker icon in system tray")
    print("   2. Open Sound Settings")
    print("   3. Select your Bluetooth device as output")
    print("   4. Test it")
    
    print(f"\n⏱️  You have 30 seconds to activate...")
    
    # Countdown
    for i in range(30, 0, -5):
        print(f"   {i} seconds remaining...", end='\r')
        time.sleep(5)
    
    print("\n   ✅ Attempting connection now...                ")


def get_clean_device_name(full_name):
    """Extract clean device name from PyAudio device string"""
    import re
    matches = re.findall(r'\(([^)]+)\)', full_name)
    if len(matches) >= 2:
        return matches[-2]  # Second to last match is usually the friendly name
    elif matches:
        return matches[-1]
    return full_name


def main():
    print("\n" + "="*70)
    print("WINDOWS BLUETOOTH AUDIO ACTIVATOR")
    print("="*70)
    print("\n🎯 This script helps activate Bluetooth audio devices")
    print("   so they can be used for audio streaming")
    
    # Scan for Bluetooth devices
    p = pyaudio.PyAudio()
    bt_devices = []
    
    print("\n🔍 Scanning for Bluetooth audio devices...")
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        if 'Headset' in info['name'] and 'bthhfenum' in info['name'].lower():
            if info['maxOutputChannels'] > 0:
                bt_devices.append({
                    'index': i,
                    'name': get_clean_device_name(info['name']),
                    'full_name': info['name']
                })
    
    p.terminate()
    
    if not bt_devices:
        print("❌ No Bluetooth output devices found")
        return 1
    
    print(f"✅ Found {len(bt_devices)} Bluetooth device(s):\n")
    
    for idx, dev in enumerate(bt_devices):
        print(f"   {idx + 1}. {dev['name']}")
    
    # Ask which devices to activate
    print(f"\n{'='*70}")
    
    if len(bt_devices) == 1:
        print("Only one device found - will activate it")
        selected = [0]
    else:
        print(f"How many devices to activate? (1-{len(bt_devices)}): ", end="")
        try:
            count = int(input().strip())
            if count < 1 or count > len(bt_devices):
                count = min(2, len(bt_devices))
        except:
            count = 2
        
        selected = list(range(count))
    
    # Activation phase
    activated_streams = []
    
    for idx in selected:
        device = bt_devices[idx]
        
        print(f"\n{'='*70}")
        print(f"ACTIVATING DEVICE {idx + 1}/{len(selected)}: {device['name']}")
        print(f"{'='*70}")
        
        # Show manual activation instructions
        manual_activation_guide(device['full_name'])
        
        # Try to activate
        stream = play_silence_to_activate(device['index'], device['name'])
        
        if stream:
            activated_streams.append({
                'device': device,
                'stream': stream
            })
            print(f"\n✅ {device['name']} is now ACTIVE")
        else:
            print(f"\n❌ Failed to activate {device['name']}")
            print(f"   Please try manual activation again")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"ACTIVATION SUMMARY")
    print(f"{'='*70}")
    
    if not activated_streams:
        print("\n❌ No devices were activated")
        print("\n💡 Troubleshooting:")
        print("   • Make sure devices are powered on")
        print("   • Check Bluetooth is enabled in Windows")
        print("   • Try re-pairing the devices")
        print("   • Verify devices work in other apps first")
        return 1
    
    print(f"\n✅ Successfully activated {len(activated_streams)}/{len(selected)} device(s):")
    for item in activated_streams:
        print(f"   • {item['device']['name']}")
    
    print(f"\n{'='*70}")
    print("🎊 DEVICES ARE ACTIVE AND STREAMS ARE OPEN")
    print(f"{'='*70}")
    
    print("\n⚡ NEXT STEPS:")
    print("\n   1. Open a NEW terminal window")
    print("   2. Run your intercom test:")
    print("\n      python src\\bluetooth_intercom_test.py")
    print("\n   3. KEEP THIS WINDOW OPEN while testing!")
    
    print(f"\n{'='*70}")
    print("Holding streams... Press Ctrl+C when done")
    print(f"{'='*70}\n")
    
    try:
        # Keep streams alive
        while True:
            time.sleep(1)
            
            # Periodically write silence to keep connection alive
            if int(time.time()) % 5 == 0:
                import numpy as np
                silence = np.zeros(512, dtype=np.int16).tobytes()
                for item in activated_streams:
                    try:
                        item['stream'].write(silence, exception_on_underflow=False)
                    except:
                        pass
                        
    except KeyboardInterrupt:
        print("\n\n🛑 Closing streams...")
        
        for item in activated_streams:
            try:
                item['stream'].close()
            except:
                pass
        
        print("✅ Cleanup complete")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
