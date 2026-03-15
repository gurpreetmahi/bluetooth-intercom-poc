"""
Bluetooth Manager - Handles Bluetooth device discovery and connection
"""

import logging
import threading
from enum import Enum
from typing import List, Optional, Callable

try:
    import win32com.client
    from comtypes import GUID
    WINDOWS_BT_AVAILABLE = True
except ImportError:
    WINDOWS_BT_AVAILABLE = False
    logging.warning("Windows Bluetooth libraries not available")


class DeviceState(Enum):
    """Bluetooth device connection states"""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    ERROR = 3


class BluetoothDevice:
    """Represents a Bluetooth audio device"""
    
    def __init__(self, name: str, address: str, alias: str = None):
        self.name = name
        self.address = address
        self.alias = alias or name
        self.state = DeviceState.DISCONNECTED
        self.audio_input = None
        self.audio_output = None
        
    def __repr__(self):
        return f"BluetoothDevice({self.alias}, {self.address}, {self.state.name})"


class BluetoothManager:
    """Manages Bluetooth device discovery and connections"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.devices: List[BluetoothDevice] = []
        self.device_a: Optional[BluetoothDevice] = None
        self.device_b: Optional[BluetoothDevice] = None
        
        if not WINDOWS_BT_AVAILABLE:
            self.logger.error("Windows Bluetooth support not available. Install pywin32 and comtypes.")
            
    def discover_devices(self) -> List[BluetoothDevice]:
        """
        Discover available Bluetooth devices
        
        Returns:
            List of discovered BluetoothDevice objects
        """
        self.logger.info("Starting Bluetooth device discovery...")
        
        if not WINDOWS_BT_AVAILABLE:
            self.logger.error("Cannot discover devices: Bluetooth libraries not available")
            return []
        
        try:
            discovered = []
            
            # Use Windows WMI to enumerate Bluetooth devices
            try:
                wmi = win32com.client.GetObject("winmgmts:")
                devices = wmi.InstancesOf("Win32_PnPEntity")
                
                for device in devices:
                    # Check if it's a Bluetooth device
                    if device.Name and "Bluetooth" in device.Name:
                        # Try to extract MAC address from device ID
                        device_id = device.DeviceID if device.DeviceID else ""
                        
                        # Simple heuristic: look for audio devices
                        if any(keyword in str(device.Name).lower() for keyword in 
                               ['headset', 'headphone', 'earbud', 'speaker', 'audio', 'hands-free']):
                            
                            # Generate a pseudo MAC address from device ID
                            # In reality, we'd need more robust parsing
                            mac_address = self._extract_mac_from_device_id(device_id)
                            
                            bt_device = BluetoothDevice(
                                name=device.Name,
                                address=mac_address,
                                alias=device.Name
                            )
                            discovered.append(bt_device)
                            self.logger.info(f"Found device: {device.Name}")
                
            except Exception as wmi_error:
                self.logger.warning(f"WMI enumeration failed: {wmi_error}")
                
                # Fallback: Return mock devices for testing
                self.logger.info("Using mock devices for testing")
                discovered = [
                    BluetoothDevice("Realme Buds T01 - Left", "AA:BB:CC:DD:EE:01", "Person A"),
                    BluetoothDevice("Realme Buds T01 - Right", "AA:BB:CC:DD:EE:02", "Person B"),
                ]
            
            if not discovered:
                self.logger.warning("No Bluetooth audio devices found")
            
            self.devices = discovered
            return discovered
            
        except Exception as e:
            self.logger.error(f"Error during device discovery: {e}", exc_info=True)
            return []
    
    def _extract_mac_from_device_id(self, device_id: str) -> str:
        """
        Extract MAC address from Windows device ID
        
        Args:
            device_id: Windows device identifier string
            
        Returns:
            MAC address string or generated placeholder
        """
        import re
        import hashlib
        
        # Try to find MAC address pattern in device ID
        mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
        match = re.search(mac_pattern, device_id)
        
        if match:
            return match.group(0).replace('-', ':').upper()
        
        # If no MAC found, generate a deterministic one from device ID
        # This is a fallback for testing purposes
        hash_obj = hashlib.md5(device_id.encode())
        hash_hex = hash_obj.hexdigest()[:12]
        mac = ':'.join([hash_hex[i:i+2] for i in range(0, 12, 2)])
        return mac.upper()
    
    def connect_device(self, device: BluetoothDevice) -> bool:
        """
        Connect to a Bluetooth device
        
        Args:
            device: BluetoothDevice to connect to
            
        Returns:
            True if connection successful, False otherwise
        """
        self.logger.info(f"Connecting to device: {device.alias}")
        device.state = DeviceState.CONNECTING
        
        try:
            # TODO: Implement actual Bluetooth connection
            # This is a placeholder
            self.logger.warning("Device connection not yet implemented")
            
            # Simulate connection
            device.state = DeviceState.CONNECTED
            self.logger.info(f"Connected to {device.alias}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {device.alias}: {e}", exc_info=True)
            device.state = DeviceState.ERROR
            return False
    
    def disconnect_device(self, device: BluetoothDevice) -> bool:
        """
        Disconnect from a Bluetooth device
        
        Args:
            device: BluetoothDevice to disconnect
            
        Returns:
            True if disconnection successful, False otherwise
        """
        self.logger.info(f"Disconnecting from device: {device.alias}")
        
        try:
            # TODO: Implement actual disconnection
            device.state = DeviceState.DISCONNECTED
            self.logger.info(f"Disconnected from {device.alias}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect from {device.alias}: {e}", exc_info=True)
            return False
    
    def set_device_a(self, device: BluetoothDevice):
        """Set and connect to Device A"""
        if self.device_a and self.device_a.state == DeviceState.CONNECTED:
            self.disconnect_device(self.device_a)
        
        self.device_a = device
        return self.connect_device(device)
    
    def set_device_b(self, device: BluetoothDevice):
        """Set and connect to Device B"""
        if self.device_b and self.device_b.state == DeviceState.CONNECTED:
            self.disconnect_device(self.device_b)
        
        self.device_b = device
        return self.connect_device(device)
    
    def get_connected_devices(self) -> List[BluetoothDevice]:
        """Get list of currently connected devices"""
        return [d for d in [self.device_a, self.device_b] if d and d.state == DeviceState.CONNECTED]
    
    def cleanup(self):
        """Cleanup and disconnect all devices"""
        self.logger.info("Cleaning up Bluetooth connections...")
        
        for device in [self.device_a, self.device_b]:
            if device and device.state == DeviceState.CONNECTED:
                self.disconnect_device(device)
