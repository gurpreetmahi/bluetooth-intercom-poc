"""
Simple POC - Test audio routing between two Bluetooth devices
"""

import pyaudio
import wave
import sys
import time
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000  # HFP Bluetooth profile rate


def list_audio_devices(p):
    """List all audio devices"""
    print("\n" + "="*60)
    print("Available Audio Devices:")
    print("="*60)
    
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        # Filter for Bluetooth Headsets (HFP)
        if 'Headset' in info['name'] and 'bthhfenum' in info['name']:
            devices.append((i, info))
            print(f"\n[{i}] {info['name']}")
            print(f"    Inputs: {info['maxInputChannels']}, Outputs: {info['maxOutputChannels']}")
            print(f"    Sample Rate: {info['defaultSampleRate']} Hz")
    
    return devices


def test_audio_routing(p, device_a_in, device_a_out, device_b_in, device_b_out):
    """
    Route audio between two devices
    
    Args:
        p: PyAudio instance
        device_a_in: Device A input (mic) index
        device_a_out: Device A output (speaker) index
        device_b_in: Device B input (mic) index  
        device_b_out: Device B output (speaker) index
    """
    logger.info("Setting up audio streams...")
    
    try:
        # Open streams for Device A
        stream_a_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_a_in,
            frames_per_buffer=CHUNK
        )
        
        stream_a_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=device_a_out,
            frames_per_buffer=CHUNK
        )
        
        # Open streams for Device B
        stream_b_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_b_in,
            frames_per_buffer=CHUNK
        )
        
        stream_b_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=device_b_out,
            frames_per_buffer=CHUNK
        )
        
        logger.info("✓ All audio streams opened successfully!")
        logger.info("Starting intercom... Press Ctrl+C to stop")
        print("\n" + "="*60)
        print("INTERCOM ACTIVE - Speak into either device!")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        # Audio routing threads
        stop_event = threading.Event()
        
        def route_a_to_b():
            """Route Device A mic to Device B speaker"""
            while not stop_event.is_set():
                try:
                    data = stream_a_in.read(CHUNK, exception_on_overflow=False)
                    stream_b_out.write(data)
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
                except Exception as e:
                    if not stop_event.is_set():
                        logger.error(f"B->A routing error: {e}")
                        break
        
        # Start routing threads
        thread_a_to_b = threading.Thread(target=route_a_to_b, daemon=True)
        thread_b_to_a = threading.Thread(target=route_b_to_a, daemon=True)
        
        thread_a_to_b.start()
        thread_b_to_a.start()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("\nStopping intercom...")
            stop_event.set()
            
            thread_a_to_b.join(timeout=2)
            thread_b_to_a.join(timeout=2)
        
        # Cleanup
        stream_a_in.stop_stream()
        stream_a_in.close()
        stream_a_out.stop_stream()
        stream_a_out.close()
        stream_b_in.stop_stream()
        stream_b_in.close()
        stream_b_out.stop_stream()
        stream_b_out.close()
        
        logger.info("Cleanup complete")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


def main():
    """Main entry point"""
    p = pyaudio.PyAudio()
    
    try:
        # List devices
        devices = list_audio_devices(p)
        
        if len(devices) < 2:
            print("\n❌ Need at least 2 Bluetooth headsets paired!")
            print("Found:", len(devices))
            return
        
        print("\n" + "="*60)
        print("Select devices for intercom:")
        print("="*60)
        
        # Find input and output pairs
        bt_devices = {}
        for idx, info in devices:
            # Extract actual device name from the complex Windows naming
            # Format: "Headset (@path;(DeviceName))"
            # We want to extract "DeviceName"
            name = info['name']
            
            # Try to find the last part in parentheses
            import re
            matches = re.findall(r'\(([^)]+)\)', name)
            if matches:
                # The device name is usually in the last parentheses
                device_name = matches[-1]
            else:
                device_name = name
            
            if info['maxInputChannels'] > 0:
                # Input device
                if device_name not in bt_devices:
                    bt_devices[device_name] = {}
                bt_devices[device_name]['input'] = idx
            if info['maxOutputChannels'] > 0:
                # Output device
                if device_name not in bt_devices:
                    bt_devices[device_name] = {}
                bt_devices[device_name]['output'] = idx
        
        # Show available complete devices
        print("\nComplete Bluetooth devices (with mic + speaker):")
        complete_devices = []
        for name, indices in bt_devices.items():
            if 'input' in indices and 'output' in indices:
                complete_devices.append((name, indices))
                print(f"  {len(complete_devices)}. {name}")
                print(f"     Input: {indices['input']}, Output: {indices['output']}")
        
        if len(complete_devices) < 2:
            print(f"\n❌ Need at least 2 complete Bluetooth devices! Found: {len(complete_devices)}")
            return
        
        # Auto-select first two devices for demo
        print(f"\n📻 Using:")
        print(f"   Device A: {complete_devices[0][0]}")
        print(f"   Device B: {complete_devices[1][0]}")
        
        device_a = complete_devices[0][1]
        device_b = complete_devices[1][1]
        
        # Start intercom
        test_audio_routing(
            p,
            device_a['input'],
            device_a['output'],
            device_b['input'],
            device_b['output']
        )
        
    finally:
        p.terminate()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
