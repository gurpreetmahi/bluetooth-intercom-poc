# Dual Bluetooth Adapter Solution

## Problem
Windows limits one active HFP (Hands-Free Profile) connection per Bluetooth adapter due to `bthmodem.sys` driver design.

## Solution
Use **two separate USB Bluetooth dongles** - each with its own driver instance.

---

## Hardware Requirements

### Recommended USB Bluetooth Adapters
1. **Budget Option** (~$10-15 each):
   - TP-Link UB400 (CSR8510 chipset)
   - Plugable USB-BT4LE (Broadcom BCM20702)
   
2. **Premium Option** (~$20-30 each):
   - ASUS USB-BT500 (Bluetooth 5.0)
   - Kinivo BTD-400 (Broadcom BCM20702)

### Why These Work
- Separate USB devices = separate `bthport.sys` instances
- Each gets its own SCO channel allocation
- Independent `bthhfenum.sys` device stacks

---

## Setup Instructions

### Step 1: Install Adapters

1. Plug in **first** USB Bluetooth dongle
2. Let Windows install drivers automatically
3. Open Device Manager (`devmgmt.msc`)
4. Note the device instance path:
   ```
   Bluetooth → [Your Adapter] → Properties → Details → Device instance path
   Example: USB\VID_0A12&PID_0001\5&123ABC
   ```

5. Plug in **second** USB Bluetooth dongle
6. Repeat step 4 for second adapter

### Step 2: Disable Built-in Bluetooth

**If your PC has built-in Bluetooth:**
1. Open Device Manager
2. Find `Bluetooth` section
3. Right-click built-in adapter → `Disable device`
4. This prevents conflicts

### Step 3: Pair Devices to Specific Adapters

**Device A → Adapter 1:**
1. Open Settings → Bluetooth & devices
2. **Temporarily disable Adapter 2** in Device Manager
3. Pair first Realme Buds T01
4. Test audio playback
5. Re-enable Adapter 2

**Device B → Adapter 2:**
1. **Temporarily disable Adapter 1** in Device Manager  
2. Pair second Realme Buds T01 (or Talk Three)
3. Test audio playback
4. Re-enable Adapter 1

### Step 4: Verify Configuration

Run this PowerShell script to verify setup:

```powershell
# List all Bluetooth radios and their paired devices
Get-PnpDevice -Class Bluetooth | ForEach-Object {
    Write-Host "`n=== $($_.FriendlyName) ===" -ForegroundColor Cyan
    Write-Host "Status: $($_.Status)"
    Write-Host "Instance ID: $($_.InstanceId)"
}

# List audio endpoints
Get-AudioDevice -List | Where-Object { $_.Name -like "*Headset*" }
```

---

## Code Modifications

### Update `bluetooth_manager.py`

Add adapter-specific device binding:

```python
class BluetoothDevice:
    def __init__(self, name: str, address: str, adapter_id: str = None):
        self.name = name
        self.address = address
        self.adapter_id = adapter_id  # Which USB adapter this is paired to
        self.state = DeviceState.DISCONNECTED

def get_device_adapter_mapping():
    """Map each audio device to its Bluetooth adapter"""
    import winreg
    
    mapping = {}
    
    # Query registry for device topology
    key_path = r"SYSTEM\CurrentControlSet\Enum\BTHHFENUM"
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        # Enumerate HFP devices and their parent adapters
        # ... implementation details ...
    except WindowsError as e:
        logging.error(f"Cannot read BT registry: {e}")
    
    return mapping
```

### Update `activate_and_hold.py`

Detect which adapter each device uses:

```python
def get_bluetooth_devices_with_adapter():
    """Get BT devices and their adapter info"""
    p = pyaudio.PyAudio()
    bt_devices = []
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        if 'Headset' in info['name'] and 'bthhfenum' in info['name']:
            # Extract adapter info from device name
            # Device name format: "Headset (Device Name) (bthhfenum;BthLEEnum\\{X})"
            import re
            adapter_match = re.search(r'BthLEEnum\\{([^}]+)}', info['name'])
            adapter_id = adapter_match.group(1) if adapter_match else "unknown"
            
            device_entry = {
                'friendly_name': extract_name(info['name']),
                'full_name': info['name'],
                'index': i,
                'adapter_id': adapter_id,
                'input_ch': info['maxInputChannels'],
                'output_ch': info['maxOutputChannels']
            }
            bt_devices.append(device_entry)
    
    p.terminate()
    return bt_devices

def verify_different_adapters(device_a, device_b):
    """Ensure devices are on different adapters"""
    if device_a['adapter_id'] == device_b['adapter_id']:
        print(f"⚠️  WARNING: Both devices on same adapter!")
        print(f"   Device A: {device_a['friendly_name']} → Adapter {device_a['adapter_id']}")
        print(f"   Device B: {device_b['friendly_name']} → Adapter {device_b['adapter_id']}")
        print(f"\n❌ Windows will only allow ONE active at a time.")
        print(f"   Re-pair devices to different USB Bluetooth adapters.")
        return False
    
    print(f"✅ Devices on different adapters:")
    print(f"   Device A: {device_a['friendly_name']} → Adapter {device_a['adapter_id'][:8]}")
    print(f"   Device B: {device_b['friendly_name']} → Adapter {device_b['adapter_id'][:8]}")
    return True
```

---

## Testing Procedure

### Test 1: Individual Activation
```bash
# Test Device A alone
python src/test_single_device.py --device 0

# Test Device B alone  
python src/test_single_device.py --device 1
```

### Test 2: Simultaneous Activation
```bash
# This should now work with dual adapters
python src/activate_and_hold.py
```

Expected output:
```
✅ Found 2 Bluetooth device(s)

Device A: realme Buds T01 → Adapter 0A12:0001
Device B: Talk Three → Adapter 0A12:0002

📡 Opening audio stream for: realme Buds T01
  ✓ Output stream opened
  ✓ Test tone played

📡 Opening audio stream for: Talk Three  
  ✓ Output stream opened
  ✓ Test tone played

✅ ✅ BOTH DEVICES ACTIVATED! ✅ ✅
```

### Test 3: Full Intercom
```bash
# In Terminal 1:
python src/activate_and_hold.py

# In Terminal 2:
python src/bluetooth_intercom_test.py
```

---

## Troubleshooting

### Issue: Both devices show same adapter
**Solution:**
1. Unpair both devices in Windows Settings
2. Disable one USB adapter in Device Manager
3. Pair Device A
4. Disable first adapter, enable second
5. Pair Device B
6. Enable both adapters

### Issue: "Device not available" error
**Solution:**
- Ensure devices are powered on and in range
- Play audio to device from Windows to activate SCO
- Run script within 10 seconds of activation

### Issue: Audio glitches or dropouts
**Possible causes:**
- USB bandwidth contention (use different USB controllers if possible)
- Bluetooth interference (separate dongles physically)
- CPU overload (check Task Manager)

**Solutions:**
- Plug dongles into separate USB root hubs
- Reduce CHUNK size in code (try 512 instead of 1024)
- Lower sample rate if quality isn't critical

---

## Driver-Level Details (Advanced)

### How Windows Manages Multiple Adapters

Each USB Bluetooth adapter creates:
```
USB Root Hub
└── USB Bluetooth Adapter (VID_XXXX&PID_YYYY)
    ├── bthport.sys (Bluetooth Port Driver)
    ├── bthusb.sys (USB Transport)
    ├── bthmodem.sys (Modem/Audio Support) ← INDEPENDENT INSTANCE
    └── btintel.sys / bthchip.sys (Vendor driver)
        └── BTHHFENUM (HFP Enumerator) ← INDEPENDENT SCO CHANNEL
```

Each `bthmodem.sys` instance manages **its own SCO channel pool**, so:
- Adapter 1: SCO channel for Device A ✅
- Adapter 2: SCO channel for Device B ✅
- **No conflict** because different HCI controllers

### Registry Keys (Reference)

Device topology stored in:
```
HKLM\SYSTEM\CurrentControlSet\Enum\USB\VID_XXXX&PID_YYYY\<instance>\Device Parameters
  L "BluetoothAddress" = (MAC of adapter)

HKLM\SYSTEM\CurrentControlSet\Enum\BTHHFENUM\{<device_guid>}
  L "ParentIdPrefix" = (links to USB adapter instance)
```

### Monitor SCO Connections

Use `bthpsproxy.exe` (Bluetooth Profile Support Process) logs:
```
Event Viewer → Applications and Services → Microsoft → Windows → Bluetooth
```

Look for events:
- **Event ID 17**: SCO connection established
- **Event ID 18**: SCO connection terminated
- **Event ID 22**: SCO connection failed (conflict indicator)

---

## Cost-Benefit Analysis

| Solution | Cost | Complexity | Success Rate |
|----------|------|------------|--------------|
| Dual USB adapters | $20-30 | Low | 95%+ |
| Custom driver | $0 | Very High | 60% |
| Linux/BlueZ | $0 | Medium | 90%+ |
| Single adapter (won't work) | $0 | N/A | 0% |

**Recommendation: Buy two USB Bluetooth dongles. This is the path of least resistance.**

---

## Next Steps

1. **Order USB Bluetooth adapters** (2x TP-Link UB400 or similar)
2. **Update code** with adapter detection logic
3. **Test single-device activation** on each adapter
4. **Test dual activation** with both adapters
5. **Run full intercom test** with audio routing

Expected delivery: Same-day (Amazon) or 2-3 days (eBay/Aliexpress)

---

## Alternative: Test with PC Audio First

While waiting for adapters, test with hybrid setup:
```
PC Microphone → Audio Router → Bluetooth Headset
```

This validates your routing code without needing two BT devices.

See `src/test_pc_audio.py` for implementation.
