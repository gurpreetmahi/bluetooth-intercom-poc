"""
Hybrid Intercom Test: PC Audio ←→ Bluetooth Device
Works within Windows single-HFP limitation
"""

import pyaudio
import numpy as np
import time
import threading
import sys


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000


def get_bluetooth_device():
    """Get first available Bluetooth headset"""
    p = pyaudio.PyAudio()
    
    print("\n🔍 Scanning for Bluetooth devices...\n")
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        if 'Headset' in info['name'] and 'bthhfenum' in info['name']:
            if info['maxOutputChannels'] > 0:
                print(f"✅ Found Bluetooth device:")
                print(f"   Name: {info['name']}")
                print(f"   Index: {i}")
                
                # Find corresponding input
                input_idx = None
                for j in range(p.get_device_count()):
                    info_j = p.get_device_info_by_index(j)
                    if info_j['name'] == info['name'] and info_j['maxInputChannels'] > 0:
                        input_idx = j
                        break
                
                p.terminate()
                return {
                    'output': i,
                    'input': input_idx,
                    'name': info['name']
                }
    
    p.terminate()
    return None


def route_pc_to_bt(pc_input, bt_output, running):
    """Route audio from PC mic to Bluetooth device"""
    try:
        while running[0]:
            data = pc_input.read(CHUNK, exception_on_overflow=False)
            bt_output.write(data)
    except Exception as e:
        print(f"❌ PC→BT error: {e}")


def route_bt_to_pc(bt_input, pc_output, running):
    """Route audio from Bluetooth device to PC speakers"""
    try:
        while running[0]:
            data = bt_input.read(CHUNK, exception_on_overflow=False)
            pc_output.write(data)
    except Exception as e:
        print(f"❌ BT→PC error: {e}")


def main():
    """Run hybrid intercom test"""
    print("\n" + "="*70)
    print("HYBRID INTERCOM TEST: PC ←→ BLUETOOTH DEVICE")
    print("="*70)
    print("\nThis test works within Windows limitations:")
    print("  • Person A: Uses PC microphone + speakers")
    print("  • Person B: Uses Bluetooth earbuds")
    print("="*70)
    
    # Get Bluetooth device
    bt_device = get_bluetooth_device()
    
    if not bt_device:
        print("\n❌ No Bluetooth device found!")
        print("\n💡 Make sure:")
        print("   • Device is paired with PC")
        print("   • Device is turned on")
        print("   • Device appears in Windows Sound settings")
        return 1
    
    if bt_device['input'] is None:
        print("\n❌ Bluetooth device has no microphone input!")
        return 1
    
    print(f"\n✅ Using Bluetooth device: {bt_device['name']}")
    
    # Ask user to activate device
    print("\n" + "="*70)
    print("ACTIVATION REQUIRED")
    print("="*70)
    print("\n📋 Before continuing:")
    print("   1. Open Settings → System → Sound")
    print("   2. Find your Bluetooth device in 'Output devices'")
    print("   3. Click on it, then click 'Test'")
    print("   4. Come back here IMMEDIATELY")
    
    response = input("\n▶️  Ready? Press Enter to continue (or 'n' to cancel): ")
    if response.lower() == 'n':
        return 0
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    print("\n" + "="*70)
    print("OPENING AUDIO STREAMS...")
    print("="*70)
    
    try:
        # PC microphone (input)
        print("\n📡 Opening PC microphone...")
        pc_input = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        print("  ✓ PC microphone ready")
        
        # PC speakers (output)
        print("\n📡 Opening PC speakers...")
        pc_output = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )
        print("  ✓ PC speakers ready")
        
        # Bluetooth output
        print(f"\n📡 Opening Bluetooth output...")
        bt_output = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=bt_device['output'],
            frames_per_buffer=CHUNK
        )
        print("  ✓ Bluetooth output ready")
        
        # Bluetooth input
        print(f"\n📡 Opening Bluetooth microphone...")
        bt_input = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=bt_device['input'],
            frames_per_buffer=CHUNK
        )
        print("  ✓ Bluetooth microphone ready")
        
    except Exception as e:
        print(f"\n❌ Failed to open audio streams: {e}")
        print("\n💡 The device might not be active. Try:")
        print("   • Click 'Test' in Windows Sound settings")
        print("   • Run this script again IMMEDIATELY")
        p.terminate()
        return 1
    
    # Start routing
    print("\n" + "="*70)
    print("✅ ✅ INTERCOM ACTIVE! ✅ ✅")
    print("="*70)
    print("\n🎤 Audio Routing:")
    print("   PC Mic → Bluetooth Earbuds")
    print("   Bluetooth Mic → PC Speakers")
    print("\n🧪 Test It:")
    print("   • Speak into PC microphone → hear in Bluetooth earbuds")
    print("   • Speak into Bluetooth microphone → hear from PC speakers")
    print("\n⚠️  Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    # Start routing threads
    running = [True]
    
    thread_pc_to_bt = threading.Thread(
        target=route_pc_to_bt,
        args=(pc_input, bt_output, running)
    )
    thread_bt_to_pc = threading.Thread(
        target=route_bt_to_pc,
        args=(bt_input, pc_output, running)
    )
    
    thread_pc_to_bt.daemon = True
    thread_bt_to_pc.daemon = True
    
    thread_pc_to_bt.start()
    thread_bt_to_pc.start()
    
    # Monitor
    try:
        start_time = time.time()
        while True:
            time.sleep(1)
            elapsed = int(time.time() - start_time)
            print(f"\r⏱️  Running: {elapsed}s", end='', flush=True)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping intercom...")
        running[0] = False
        time.sleep(0.5)
        
        # Close streams
        pc_input.close()
        pc_output.close()
        bt_input.close()
        bt_output.close()
        p.terminate()
        
        print("✅ Intercom stopped\n")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
