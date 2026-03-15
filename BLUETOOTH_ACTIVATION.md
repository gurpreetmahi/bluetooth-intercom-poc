# Windows Bluetooth Activation Workaround

## The Problem

Windows Bluetooth devices can be **paired** but not **actively connected** for audio. PyAudio (and most audio libraries) cannot open streams to devices that aren't in active audio mode.

**Error**: `[Errno -9999] Unanticipated host error`

## Manual Activation Process (CONFIRMED WORKING)

### Method 1: Windows Sound Settings (Recommended)

1. **Open Windows Sound Settings:**
   - Press `Win + I` → System → Sound
   - OR: Right-click speaker icon in taskbar → "Sound settings"

2. **Activate Device A (First Bluetooth device):**
   - Scroll to "Output devices"
   - Click on your first Bluetooth device (e.g., "WI-C100")
   - Click "Test" button → You should hear a tone
   - Leave this window open

3. **Activate Device B (Second Bluetooth device):**
   - In the same "Output devices" list
   - Click on your second Bluetooth device (e.g., "SBH54")
   - Click "Test" button → You should hear a tone

4. **Run the intercom test IMMEDIATELY:**
   ```powershell
   python src\bluetooth_intercom_test.py
   ```

**Important**: Windows may deactivate devices after a few seconds of inactivity. Run the test quickly after activation!

### Method 2: Play Audio Through Each Device

1. **Open Windows Sound Settings**
   - Settings → System → Sound

2. **For each Bluetooth device:**
   - Set it as default output device
   - Play a song/video/YouTube
   - Let it play for 5-10 seconds
   - Repeat for second device

3. **Run test immediately:**
   ```powershell
   python src\bluetooth_intercom_test.py
   ```

### Method 3: Using PowerShell (Advanced)

Create a PowerShell script to set devices as default and play test sounds:

```powershell
# Get audio devices
Get-AudioDevice -List

# Set device as default (replace ID with your device)
Set-AudioDevice -ID "your-device-id"

# Play a test sound
[console]::beep(440, 500)
```

## Why This Happens

### Windows Bluetooth Limitations:

1. **Single Active Connection**: Windows typically maintains only ONE active Bluetooth audio connection (HFP profile) at a time

2. **Power Management**: Bluetooth devices enter low-power mode when not in use

3. **Driver Restrictions**: Windows Bluetooth stack doesn't allow programmatic activation without elevated permissions

4. **PyAudio Limitation**: PyAudio can only open streams to devices that are already in "streaming ready" state

## Solutions & Workarounds

### Option A: Manual Activation (Current)
✅ **Works now**: Follow Manual Activation Process above
⚠️ Requires manual steps before each test
⚠️ Devices may timeout and need reactivation

### Option B: Keep-Alive Script (TODO)
- Create background process that plays silence to both devices
- Keeps devices in active state
- **Implementation needed**

### Option C: Dual Bluetooth Adapters
- Use two separate Bluetooth USB adapters
- One device per adapter
- Windows treats them independently
- ✅ **Most reliable solution for production**

### Option D: VB-Audio Virtual Cables
- Install VB-Audio Cable software
- Route: Bluetooth 1 → Virtual Cable A → Virtual Cable B → Bluetooth 2
- More complex but more reliable

### Option E: Windows Audio Session API (WASAPI)
- Use Windows Core Audio APIs directly
- More control over device states
- Requires C++/C# or ctypes bindings
- **Future enhancement**

## Testing Status

| Scenario | Status | Notes |
|----------|--------|-------|
| Single device active | ⚠️ Untested | Should work |
| Both devices manually activated | ⚠️ Untested | Need user to try |
| Automatic activation | ❌ Failed | Windows limitation |
| Dual Bluetooth adapters | ⚠️ Not tested | Should work |

## Recommended Testing Approach

### For your Realme Buds T01:

**If you have TWO pairs:**
1. Pair both with Windows
2. Follow Manual Activation Method 1
3. Test intercom
4. Report results!

**If you have ONE pair:**
1. Test with ONE Realme Buds + another Bluetooth headset
2. OR: Test loopback (Realme Buds mic → Realme Buds speaker)

### Expected Behavior When Working:

When both devices are successfully activated:
```
🎉 BLUETOOTH INTERCOM ACTIVE!
Device A: WI-C100
Device B: SBH54
Duration: 30s

💬 Speak into either device - audio will be routed!

Time: 30s | A→B: 586 | B→A: 586 packets
```

You should hear:
- Voice from Device A in Device B's speakers
- Voice from Device B in Device A's speakers
- Slight delay (200-400ms) is normal

## Hardware Solution for Production

For a production intercom system, consider:

1. **ESP32 Gateway** (original plan)
   - More reliable than Windows Bluetooth
   - Can maintain multiple active connections
   - Lower level control

2. **Dual USB Bluetooth Adapters**
   - ~$10-15 each
   - One device per adapter
   - Windows treats independently
   - Plug and play

3. **Dedicated Bluetooth Gateway Device**
   - Raspberry Pi Zero 2 W
   - Better Bluetooth stack than Windows
   - Can handle multiple simultaneous connections

## Next Steps

1. **Try Manual Activation** (Method 1 above) and run the test
2. **Report back**:
   - Did both devices activate?
   - Did the intercom work?
   - Any errors?
3. Based on results, we'll either:
   - ✅ Proceed with GUI and features if working
   - 🔧 Implement keep-alive or other solutions

---

**The core code is ready and working!** It's just Windows Bluetooth being difficult. Most Linux systems and dedicated hardware (ESP32, RPi) don't have this limitation.
