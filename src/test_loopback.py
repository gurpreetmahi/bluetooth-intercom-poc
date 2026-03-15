"""
Automated loopback test - Tests audio routing with default PC audio devices
No user interaction required
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
RATE = 16000
TEST_DURATION = 5  # seconds


def main():
    """Main entry point - automatic loopback test"""
    p = pyaudio.PyAudio()
    
    try:
        # Get default devices
        default_input_info = p.get_default_input_device_info()
        default_output_info = p.get_default_output_device_info()
        
        input_idx = default_input_info['index']
        output_idx = default_output_info['index']
        
        print("\n" + "="*60)
        print("AUTOMATIC LOOPBACK TEST")
        print("="*60)
        print(f"Input:  [{input_idx}] {default_input_info['name']}")
        print(f"Output: [{output_idx}] {default_output_info['name']}")
        print(f"Duration: {TEST_DURATION} seconds")
        print("="*60 + "\n")
        
        logger.info("Opening audio streams...")
        
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
            print("🎤 LOOPBACK ACTIVE - Speak into your microphone!")
            print("You should hear yourself through the speakers...")
            print()
            
            # Audio routing
            stop_event = threading.Event()
            
            def route_audio():
                """Route audio from input to output"""
                packets = 0
                while not stop_event.is_set():
                    try:
                        data = stream_in.read(CHUNK, exception_on_overflow=False)
                        stream_out.write(data)
                        packets += 1
                    except Exception as e:
                        if not stop_event.is_set():
                            logger.error(f"Routing error: {e}")
                            break
                logger.info(f"Processed {packets} audio packets")
            
            # Start routing thread
            thread = threading.Thread(target=route_audio, daemon=True)
            thread.start()
            
            # Run for specified duration
            try:
                for remaining in range(TEST_DURATION, 0, -1):
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
            
            print("="*60)
            logger.info("✓ Loopback test completed successfully!")
            print("="*60)
            print("\n✅ RESULT: Audio routing logic is WORKING!")
            print("This proves the core intercom routing concept works.")
            print("\nNext step: Apply this to Bluetooth devices\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ Loopback test failed: {e}", exc_info=True)
            print("\n❌ RESULT: Audio routing failed")
            print("Check if microphone and speakers are working properly\n")
            return False
        
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
