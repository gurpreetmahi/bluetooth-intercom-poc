"""
Bluetooth Diagnostics - Check your adapter configuration

This script helps diagnose Windows Bluetooth adapter and device configuration
to determine if dual-device operation is possible.
"""

import pyaudio
import re
import sys
from colorama import Fore, Style, init

# Initialize colorama for Windows
init(autoreset=True)


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
    print("="*70)


def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")


def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")


def print_warning(text):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")


def extract_adapter_id(device_name):
    """Extract adapter identifier from device name"""
    # Look for bthhfenum path
    match = re.search(r'bthhfenum[^)]*', device_name, re.IGNORECASE)
    if match:
        path = match.group(0)
        # Extract GUID or unique part
        guid_match = re.search(r'\{([^}]+)\}', path)
        if guid_match:
            guid = guid_match.group(1)
            # Return first 8 chars for readability
            return guid[:8].upper()
    
    # Fallback: use simple hash of device string
    return hex(abs(hash(device_name)) % 10000)[2:].upper()


def main():
    print_header("BLUETOOTH DIAGNOSTICS - ADAPTER CONFIGURATION CHECK")
    
    print("\n📋 This diagnostic will:")
    print("   1. Detect all Bluetooth audio devices")
    print("   2. Identify which adapter each device uses")
    print("   3. Determine if dual-device operation is possible")
    print("   4. Provide recommendations")
    
    # Get all audio devices
    p = pyaudio.PyAudio()
    
    print_header("SCANNING AUDIO DEVICES")
    
    bluetooth_devices = []
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        # Look for Bluetooth HFP devices
        if 'Headset' in info['name'] and ('bthhfenum' in info['name'].lower() or 'bluetooth' in info['name'].lower()):
            # Extract friendly name
            matches = re.findall(r'\(([^)]+)\)', info['name'])
            if matches:
                friendly_name = matches[-2] if len(matches) >= 2 else matches[-1]
            else:
                friendly_name = info['name']
            
            # Extract adapter ID
            adapter_id = extract_adapter_id(info['name'])
            
            bluetooth_devices.append({
                'index': i,
                'friendly_name': friendly_name,
                'full_name': info['name'],
                'adapter_id': adapter_id,
                'input_channels': info['maxInputChannels'],
                'output_channels': info['maxOutputChannels'],
                'sample_rate': int(info['defaultSampleRate'])
            })
    
    p.terminate()
    
    if not bluetooth_devices:
        print_error("No Bluetooth audio devices found!")
        print("\n💡 Make sure:")
        print("   • Bluetooth devices are paired")
        print("   • Devices are powered on")
        print("   • Devices show up in Windows Sound Settings")
        return 1
    
    print_success(f"Found {len(bluetooth_devices)} Bluetooth device(s)")
    
    # Group by adapter
    print_header("DEVICE → ADAPTER MAPPING")
    
    adapters = {}
    for device in bluetooth_devices:
        adapter_id = device['adapter_id']
        if adapter_id not in adapters:
            adapters[adapter_id] = []
        adapters[adapter_id].append(device)
    
    print(f"\n📡 Detected {len(adapters)} Bluetooth adapter(s):\n")
    
    for i, (adapter_id, devices) in enumerate(adapters.items(), 1):
        print(f"{Fore.CYAN}▶ Adapter #{i} (ID: {adapter_id}){Style.RESET_ALL}")
        for device in devices:
            io_type = []
            if device['input_channels'] > 0:
                io_type.append(f"Input: {device['input_channels']}ch")
            if device['output_channels'] > 0:
                io_type.append(f"Output: {device['output_channels']}ch")
            
            print(f"   • {device['friendly_name']}")
            print(f"     {', '.join(io_type)}, {device['sample_rate']} Hz")
        print()
    
    # Analysis
    print_header("CONFIGURATION ANALYSIS")
    
    output_devices = [d for d in bluetooth_devices if d['output_channels'] > 0]
    unique_adapters = len(adapters)
    
    print(f"\n📊 Summary:")
    print(f"   • Total BT devices: {len(bluetooth_devices)}")
    print(f"   • Devices with output: {len(output_devices)}")
    print(f"   • Unique adapters: {unique_adapters}")
    
    # Determine if dual-device operation is possible
    print_header("DUAL-DEVICE CAPABILITY ASSESSMENT")
    
    if len(output_devices) < 2:
        print_error("INSUFFICIENT DEVICES")
        print("\n   Need: 2+ Bluetooth devices with output capability")
        print(f"   Found: {len(output_devices)}")
        print("\n💡 Pair another Bluetooth headset/speaker")
        return 1
    
    if unique_adapters == 1:
        print_error("SINGLE ADAPTER LIMITATION - DUAL DEVICES WILL NOT WORK")
        print("\n   ❌ All devices are using the SAME Bluetooth adapter")
        print("   ❌ Windows only allows 1 active HFP connection per adapter")
        print("   ❌ Opening second device will fail with error -9999")
        
        print_header("💡 SOLUTION: INSTALL DUAL USB BLUETOOTH ADAPTERS")
        
        print("\n🛒 What to buy:")
        print("   • 2x USB Bluetooth adapters (dongles)")
        print("   • Recommended models:")
        print("     - TP-Link UB400 (~$10)")
        print("     - Plugable USB-BT4LE (~$13)")
        print("     - ASUS USB-BT500 (~$20)")
        
        print("\n📝 Setup steps:")
        print("   1. Buy 2x USB Bluetooth dongles")
        print("   2. Disable built-in Bluetooth (if any)")
        print("   3. Plug in first dongle")
        print("   4. Unpair Device A, then re-pair to first dongle")
        print("   5. Plug in second dongle")
        print("   6. Pair Device B to second dongle")
        print("   7. Run this diagnostic again")
        
        print("\n📄 Detailed guide:")
        print("   See: DUAL_ADAPTER_SOLUTION.md")
        
        print_header("CURRENT STATUS: ❌ NOT READY")
        return 1
    
    else:
        print_success("MULTIPLE ADAPTERS DETECTED!")
        print("\n   ✅ You have multiple Bluetooth adapters")
        print("   ✅ Devices are spread across adapters")
        print("   ✅ Dual-device operation SHOULD work!")
        
        # Check if first two output devices are on different adapters
        if len(output_devices) >= 2:
            dev_a = output_devices[0]
            dev_b = output_devices[1]
            
            if dev_a['adapter_id'] != dev_b['adapter_id']:
                print_success(f"Device pairing looks good:")
                print(f"       • {dev_a['friendly_name']} → Adapter {dev_a['adapter_id']}")
                print(f"       • {dev_b['friendly_name']} → Adapter {dev_b['adapter_id']}")
                
                print_header("CURRENT STATUS: ✅ READY FOR DUAL-DEVICE OPERATION")
                
                print("\n🚀 Next steps:")
                print("   1. Run: python src\\activate_and_hold.py")
                print("   2. If successful, run: python src\\bluetooth_intercom_test.py")
                
                return 0
            else:
                print_warning("First two devices on SAME adapter")
                print(f"\n   Device A: {dev_a['friendly_name']} → Adapter {dev_a['adapter_id']}")
                print(f"   Device B: {dev_b['friendly_name']} → Adapter {dev_b['adapter_id']}")
                print("\n   💡 Re-pair one device to the other adapter:")
                
                # Find which adapter has space
                for adapter_id, devices in adapters.items():
                    if adapter_id != dev_a['adapter_id']:
                        print(f"\n   Steps to move {dev_b['friendly_name']}:")
                        print(f"   1. Unpair {dev_b['friendly_name']} from Windows")
                        print(f"   2. In Device Manager, disable Adapter {dev_a['adapter_id']}")
                        print(f"   3. Re-pair {dev_b['friendly_name']} (will use Adapter {adapter_id})")
                        print(f"   4. Enable Adapter {dev_a['adapter_id']} again")
                        print(f"   5. Run this diagnostic again")
                        break
                
                print_header("CURRENT STATUS: ⚠️  NEEDS RECONFIGURATION")
                return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Diagnostic cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
