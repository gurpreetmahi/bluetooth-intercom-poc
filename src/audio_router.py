"""
Audio Router - Handles audio capture, routing, and playback between devices
"""

import logging
import threading
import queue
import numpy as np
from typing import Optional

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("PyAudio not available")


class AudioRouter:
    """Routes audio between two Bluetooth devices"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Audio settings
        self.sample_rate = config['audio']['sample_rate']
        self.channels = config['audio']['channels']
        self.chunk_size = config['audio']['chunk_size']
        
        # PyAudio instance
        self.audio = None
        if AUDIO_AVAILABLE:
            self.audio = pyaudio.PyAudio()
        else:
            self.logger.error("PyAudio not available. Audio routing disabled.")
        
        # Audio streams
        self.stream_a_input = None
        self.stream_a_output = None
        self.stream_b_input = None
        self.stream_b_output = None
        
        # Audio queues for buffering
        self.queue_a_to_b = queue.Queue(maxsize=50)
        self.queue_b_to_a = queue.Queue(maxsize=50)
        
        # Routing control
        self.routing_active = False
        self.routing_threads = []
        self.stop_event = threading.Event()
        
        # PTT state
        self.ptt_active = False
        
    def list_audio_devices(self):
        """List all available audio devices"""
        if not self.audio:
            self.logger.error("PyAudio not initialized")
            return []
        
        devices = []
        for i in range(self.audio.get_device_count()):
            try:
                info = self.audio.get_device_info_by_index(i)
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'input_channels': info['maxInputChannels'],
                    'output_channels': info['maxOutputChannels'],
                    'sample_rate': info['defaultSampleRate']
                })
            except Exception as e:
                self.logger.warning(f"Error getting device {i}: {e}")
        
        return devices
    
    def setup_audio_streams(self, device_a_index: int, device_b_index: int):
        """
        Setup audio input/output streams for both devices
        
        Args:
            device_a_index: PyAudio device index for Device A
            device_b_index: PyAudio device index for Device B
        """
        if not self.audio:
            self.logger.error("Cannot setup streams: PyAudio not available")
            return False
        
        try:
            # Device A streams
            self.stream_a_input = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_a_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.stream_a_output = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=device_a_index,
                frames_per_buffer=self.chunk_size
            )
            
            # Device B streams
            self.stream_b_input = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_b_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.stream_b_output = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=device_b_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.logger.info("Audio streams setup successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup audio streams: {e}", exc_info=True)
            return False
    
    def start_routing(self):
        """Start audio routing between devices"""
        if self.routing_active:
            self.logger.warning("Audio routing already active")
            return
        
        if not all([self.stream_a_input, self.stream_a_output, 
                   self.stream_b_input, self.stream_b_output]):
            self.logger.error("Audio streams not setup. Call setup_audio_streams() first.")
            return
        
        self.logger.info("Starting audio routing...")
        self.routing_active = True
        self.stop_event.clear()
        
        # Create routing threads
        thread_a_to_b = threading.Thread(target=self._route_a_to_b, daemon=True)
        thread_b_to_a = threading.Thread(target=self._route_b_to_a, daemon=True)
        
        self.routing_threads = [thread_a_to_b, thread_b_to_a]
        
        thread_a_to_b.start()
        thread_b_to_a.start()
        
        self.logger.info("Audio routing started")
    
    def stop_routing(self):
        """Stop audio routing"""
        if not self.routing_active:
            return
        
        self.logger.info("Stopping audio routing...")
        self.routing_active = False
        self.stop_event.set()
        
        # Wait for threads to finish
        for thread in self.routing_threads:
            thread.join(timeout=2.0)
        
        self.routing_threads = []
        self.logger.info("Audio routing stopped")
    
    def _route_a_to_b(self):
        """Route audio from Device A to Device B"""
        self.logger.debug("Starting A->B routing thread")
        
        while self.routing_active and not self.stop_event.is_set():
            try:
                # Read from Device A microphone
                audio_data = self.stream_a_input.read(self.chunk_size, exception_on_overflow=False)
                
                # Apply VOX or PTT logic
                if self.config['ptt']['enabled'] and not self.ptt_active:
                    # Mute if PTT not active
                    audio_data = b'\x00' * len(audio_data)
                
                # Write to Device B speaker
                self.stream_b_output.write(audio_data)
                
            except Exception as e:
                if self.routing_active:
                    self.logger.error(f"Error in A->B routing: {e}")
    
    def _route_b_to_a(self):
        """Route audio from Device B to Device A"""
        self.logger.debug("Starting B->A routing thread")
        
        while self.routing_active and not self.stop_event.is_set():
            try:
                # Read from Device B microphone
                audio_data = self.stream_b_input.read(self.chunk_size, exception_on_overflow=False)
                
                # Always allow B->A (for full duplex, adjust as needed)
                
                # Write to Device A speaker
                self.stream_a_output.write(audio_data)
                
            except Exception as e:
                if self.routing_active:
                    self.logger.error(f"Error in B->A routing: {e}")
    
    def set_ptt(self, active: bool):
        """Set Push-To-Talk state"""
        self.ptt_active = active
        self.logger.debug(f"PTT: {'ON' if active else 'OFF'}")
    
    def get_audio_level(self, device: str) -> float:
        """
        Get current audio level for a device
        
        Args:
            device: 'a' or 'b'
            
        Returns:
            Audio level 0.0 to 1.0
        """
        # TODO: Implement actual audio level detection
        return 0.0
    
    def cleanup(self):
        """Cleanup audio resources"""
        self.logger.info("Cleaning up audio resources...")
        
        self.stop_routing()
        
        # Close streams
        for stream in [self.stream_a_input, self.stream_a_output,
                      self.stream_b_input, self.stream_b_output]:
            if stream:
                stream.stop_stream()
                stream.close()
        
        # Terminate PyAudio
        if self.audio:
            self.audio.terminate()
        
        self.logger.info("Audio cleanup complete")
