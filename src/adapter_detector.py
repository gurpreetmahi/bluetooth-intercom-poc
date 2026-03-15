"""
Bluetooth Adapter Detection - Identifies which USB adapter each device uses
"""

import re
import logging
from typing import Dict, List, Optional

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False
    logging.warning("winreg not available")


def get_adapter_info() -> Dict[str, any]:
    """
    Get information about all Bluetooth adapters in the system
    
    Returns:
        Dictionary mapping adapter IDs to adapter info
    """
    if not WINREG_AVAILABLE:
        return {}
    
    adapters = {}
    
    try:
        # Enumerate USB Bluetooth devices
        key_path = r"SYSTEM\CurrentControlSet\Enum\USB"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                
                # Look for Bluetooth adapters (various VID/PID combinations)
                if any(vid in subkey_name.upper() for vid in ['0A12', '8087', '0CF3', '13D3']):
                    # This might be a Bluetooth adapter
                    try:
                        device_key = winreg.OpenKey(key, subkey_name)
                        
                        # Get first instance
                        j = 0
                        while True:
                            try:
                                instance = winreg.EnumKey(device_key, j)
                                instance_path = f"{subkey_name}\\{instance}"
                                
                                # Try to get device description
                                try:
                                    instance_key = winreg.OpenKey(device_key, instance)
                                    desc, _ = winreg.QueryValueEx(instance_key, "DeviceDesc")
                                    
                                    if 'bluetooth' in desc.lower():
                                        adapter_id = f"{subkey_name}_{j}"
                                        adapters[adapter_id] = {
                                            'instance_path': instance_path,
                                            'description': desc,
                                            'vid_pid': subkey_name
                                        }
                                    
                                    winreg.CloseKey(instance_key)
                                except WindowsError:
                                    pass
                                
                                j += 1
                            except WindowsError:
                                break
                        
                        winreg.CloseKey(device_key)
                    except WindowsError:
                        pass
                
                i += 1
            except WindowsError:
                break
        
        winreg.CloseKey(key)
        
    except Exception as e:
        logging.error(f"Error enumerating adapters: {e}")
    
    return adapters


def extract_adapter_from_device_name(device_name: str) -> Optional[str]:
    """
    Extract adapter identifier from PyAudio device name
    
    PyAudio device names for Bluetooth HFP look like:
    "Headset (Device Name) (bthhfenum;BthLEEnum\\{GUID}\\...)"
    or
    "Headset Microphone (Device Name) (bthhfenum)"
    
    Args:
        device_name: Full PyAudio device name
        
    Returns:
        Adapter identifier or None
    """
    # Try to extract from bthhfenum path
    match = re.search(r'bthhfenum(?:;.*?\\{([^}]+)})?', device_name.lower())
    if match and match.group(1):
        return match.group(1)
    
    # Fallback: use device name as identifier
    # In practice, devices on same adapter will have similar paths
    match = re.search(r'\(([^)]+)\)$', device_name)
    if match:
        path = match.group(1)
        # Extract meaningful part of path
        if '\\' in path:
            parts = path.split('\\')
            # Return last few parts as identifier
            return '_'.join(parts[-2:]) if len(parts) >= 2 else parts[-1]
    
    return None


def check_devices_on_different_adapters(device_a_name: str, device_b_name: str) -> bool:
    """
    Check if two devices are on different Bluetooth adapters
    
    Args:
        device_a_name: PyAudio device name for first device
        device_b_name: PyAudio device name for second device
        
    Returns:
        True if devices are on different adapters, False if same adapter or cannot determine
    """
    adapter_a = extract_adapter_from_device_name(device_a_name)
    adapter_b = extract_adapter_from_device_name(device_b_name)
    
    print(f"\n🔍 Adapter Detection:")
    print(f"   Device A adapter: {adapter_a or 'Unknown'}")
    print(f"   Device B adapter: {adapter_b or 'Unknown'}")
    
    if adapter_a is None or adapter_b is None:
        print(f"   ⚠️  Cannot determine adapter assignment")
        return None
    
    if adapter_a == adapter_b:
        print(f"   ❌ SAME ADAPTER - Windows will block simultaneous use!")
        return False
    else:
        print(f"   ✅ DIFFERENT ADAPTERS - Simultaneous use should work!")
        return True


def list_bluetooth_adapters():
    """
    List all Bluetooth adapters detected in the system
    """
    print("\n" + "="*70)
    print("BLUETOOTH ADAPTER DETECTION")
    print("="*70)
    
    adapters = get_adapter_info()
    
    if not adapters:
        print("\n⚠️  Could not detect Bluetooth adapters via registry")
        print("   This is normal on some systems")
        print("   Device-level detection will be used instead")
        return
    
    print(f"\n✅ Found {len(adapters)} Bluetooth adapter(s):\n")
    
    for adapter_id, info in adapters.items():
        print(f"  📡 {info['description']}")
        print(f"     VID/PID: {info['vid_pid']}")
        print(f"     Instance: {info['instance_path']}")
        print()
    
    if len(adapters) < 2:
        print("⚠️  IMPORTANT: Only 1 Bluetooth adapter detected")
        print("   Windows limits 1 active HFP connection per adapter")
        print("\n   💡 To use 2 Bluetooth devices simultaneously:")
        print("      • Buy 2x USB Bluetooth dongles ($10-15 each)")
        print("      • See DUAL_ADAPTER_SOLUTION.md for details")


if __name__ == "__main__":
    # Test the detection
    list_bluetooth_adapters()
    
    # Test device comparison
    print("\n" + "="*70)
    print("DEVICE COMPARISON TEST")
    print("="*70)
    
    # Example device names (you'll need to replace with actual names)
    test_device_a = "Headset (realme Buds T01) (bthhfenum;{12345678-abcd-ef00-1234-567890abcdef})"
    test_device_b = "Headset (Talk Three) (bthhfenum;{87654321-dcba-00fe-4321-fedcba098765})"
    
    print(f"\nTest Device A: {test_device_a}")
    print(f"Test Device B: {test_device_b}")
    
    check_devices_on_different_adapters(test_device_a, test_device_b)
