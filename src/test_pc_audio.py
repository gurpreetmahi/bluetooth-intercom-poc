"""
Test audio routing with regular PC audio devices (not Bluetooth)
This proves the routing logic works before tackling Bluetooth challenges
"""

import pyaudio
import threading
import time
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Standard sample rate


def list_audio_devices(p):
    """List all audio devices"""
    print("\n" + "="*60)
    print("Available Audio Devices:")
    print("="*60)
    
    input_devices = []
    output_devices = []
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        if info['maxInputChannels'] > 0 and 'Microsoft Sound Mapper' not in info['name']:
            input_devices.append((i, info))
            
        if info['maxOutputChannels'] > 0 and 'Microsoft Sound Mapper' not in info['name']:
            output_devices.append((i, info))
    
    print("\nINPUT Devices (Microphones):")
    for i, (idx, info) in enumerate(input_devices, 1):
        default = " [DEFAULT]" if idx == p.get_default_input_device_info()['index'] else ""
        print(f"  {i}. [{idx}] {info['name']}{default}")
    
    print("\nOUTPUT Devices (Speakers):")
    for i, (idx, info) in enumerate(output_devices, 1):
        default = " [DEFAULT]" if idx == p.get_default_output_device_info()['index'] else ""
        print(f"  {i}. [{idx}] {info['name']}{default}")
    
    return input_devices, output_devices


def test_loopback(p, input_idx, output_idx, duration=10):
    """
    Test audio loopback: mic -> speaker on same device
    
    Args:
        p: PyAudio instance
        input_idx: Input device index
        output_idx: Output device index
        duration: Test duration in seconds
    """
    logger.info(f"Testing loopback: Device {input_idx} -> Device {output_idx}")
    
    try:
        # Open input stream
        stream_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=input_idx,
            frames_per_buffer=CHUNK
        )
        
        # Open output stream
        stream_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=output_idx,
            frames_per_buffer=CHUNK
        )
        
        logger.info("✓ Audio streams opened successfully!")
        print("\n" + "="*60)
        print(f"🎤 LOOPBACK TEST ACTIVE - Duration: {duration}s")
        print("Speak into your microphone - you should hear yourself!")
        print("="*60 + "\n")
        
        # Audio routing
        stop_event = threading.Event()
        
        def route_audio():
            """Route audio from input to output"""
            while not stop_event.is_set():
                try:
                    data = stream_in.read(CHUNK, exception_on_overflow=False)
                    stream_out.write(data)
                except Exception as e:
                    if not stop_event.is_set():
                        logger.error(f"Routing error: {e}")
                        break
        
        # Start routing thread
        thread = threading.Thread(target=route_audio, daemon=True)
        thread.start()
        
        # Run for specified duration
        try:
            for remaining in range(duration, 0, -1):
                print(f"\rTime remaining: {remaining}s ", end='', flush=True)
                time.sleep(1)
            print("\n")
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        
        # Stop routing
        stop_event.set()
        thread.join(timeout=2)
        
        # Cleanup
        stream_in.stop_stream()
        stream_in.close()
        stream_out.stop_stream()
        stream_out.close()
        
        logger.info("✓ Loopback test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Loopback test failed: {e}", exc_info=True)
        return False


def test_cross_routing(p, input_a_idx, output_a_idx, input_b_idx, output_b_idx, duration=10):
    """
    Test cross-routing: Device A mic -> Device B speaker AND Device B mic -> Device A speaker
    
    This simulates the intercom scenario with regular PC audio devices
    """
    logger.info("Testing cross-routing between two devices...")
    
    try:
        # Open all streams
        stream_a_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=input_a_idx,
            frames_per_buffer=CHUNK
        )
        
        stream_a_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=output_a_idx,
            frames_per_buffer=CHUNK
        )
        
        stream_b_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=input_b_idx,
            frames_per_buffer=CHUNK
        )
        
        stream_b_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=output_b_idx,
            frames_per_buffer=CHUNK
        )
        
        logger.info("✓ All audio streams opened successfully!")
        print("\n" + "="*60)
        print(f"🎤 CROSS-ROUTING TEST ACTIVE - Duration: {duration}s")
        print("Device A mic -> Device B speaker")
        print("Device B mic -> Device A speaker")
        print("="*60 + "\n")
        
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
        
        # Run for specified duration
        try:
            for remaining in range(duration, 0, -1):
                print(f"\rTime remaining: {remaining}s ", end='', flush=True)
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
        
        logger.info("✓ Cross-routing test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cross-routing test failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point"""
    p = pyaudio.PyAudio()
    
    try:
        input_devices, output_devices = list_audio_devices(p)
        
        if not input_devices:
            print("\n❌ No input devices found!")
            return
        
        if not output_devices:
            print("\n❌ No output devices found!")
            return
        
        print("\n" + "="*60)
        print("Test Options:")
        print("="*60)
        print("1. Simple loopback test (mic -> speaker)")
        print("2. Cross-routing test (2 devices)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Simple loopback test with default devices
            print("\nUsing default input and output devices...")
            default_input = p.get_default_input_device_info()['index']
            default_output = p.get_default_output_device_info()['index']
            
            duration = input("Test duration in seconds (default 10): ").strip()
            duration = int(duration) if duration else 10
            
            test_loopback(p, default_input, default_output, duration)
            
        elif choice == '2':
            print("\n❌ Cross-routing test requires 2 separate audio devices")
            print("This is more complex - for now, test loopback first")
            
        elif choice == '3':
            print("Exiting...")
        else:
            print("Invalid choice")
        
    finally:
        p.terminate()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
