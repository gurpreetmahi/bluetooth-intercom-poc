# Quick Test Guide

## ✅ What's Working Now

### Test 1: Loopback Test (VERIFIED ✓)
Tests basic audio routing with your PC microphone and speakers:
```bash
cd c:\Users\gurpr\source\github\bluetooth-intercom-poc
python src\test_loopback.py
```
**Result**: ✅ **SUCCESSFUL** - Audio routing logic works perfectly!

### Test 2: Bluetooth Intercom Test (READY TO TEST)
Tests intercom between two Bluetooth headsets:
```bash
python src\bluetooth_intercom_test.py
```

## 🎯 Next: Test Your Realme Buds

### Prerequisites
You need **2 pairs** of Realme Buds T01 for the full intercom test.

### Steps to Test:

1. **Pair both Realme Buds pairs** with your PC:
   - Settings → Bluetooth → Add device
   - Pair first pair (name: "Realme Buds T01")
   - Pair second pair (name: "Realme Buds T01")

2. **Activate both devices for audio**:
   - Go to Settings → Sound
   - Select first Realme Buds, play test sound
   - Select second Realme Buds, play test sound
   - Both should show as "Connected" with audio

3. **Run the Bluetooth intercom test**:
   ```bash
   python src\bluetooth_intercom_test.py
   ```

4. **If it says devices "NOT available"**:
   - The script will prompt you to activate them
   - Play music/audio through each device first
   - Then respond 'y' when prompted

5. **If successful**: 🎉
   - Speak into Person A's buds → Hear in Person B's buds
   - Speak into Person B's buds → Hear in Person A's buds
   - **Intercom working!**

## 🔧 Troubleshooting

### "No Bluetooth headsets found"
- Make sure devices are paired in Windows
- Bluetooth must be ON
- Devices should appear in Sound settings

### "PyAudio error -9999"
**Most common issue!** Means devices are paired but not in active audio mode.

**Solution:**
1. Open Windows Settings → Sound
2. Click on first Realme Buds device
3. Click "Test" to play a sound
4. Repeat for second Realme Buds device
5. Both should now be "active" for audio
6. Run the test again immediately

### "Only 1 complete device found"
- Windows may only show one Realme Buds pair as active
- This is a Windows limitation
- Try: Disconnect one pair completely, then reconnect

### Windows Bluetooth Limitation
Windows typically maintains active audio connection to **ONE** Bluetooth device at a time. Getting **TWO** simultaneously active is the challenge.

**Workarounds:**
- Use Bluetooth dongles (one device per dongle)
- Use different device types (e.g., one Realme Buds + one other brand)
- Enterprise Bluetooth adapters support multiple connections

## 📊 Current Test Results

| Test | Status | Result |
|------|--------|--------|
| Audio routing logic | ✅ PASS | Verified with PC audio |
| Bluetooth device detection | ✅ PASS | Detects 3 headsets |
| Device pairing logic | ✅ PASS | Correctly pairs in/out |
| Single BT device active | ⚠️ PENDING | Need to test |
| Dual BT devices active | ⚠️ PENDING | Main challenge |

## 💡 Alternative: Test with What You Have

If you only have **1 pair of Realme Buds** right now:

### Option A: Test with mixed devices
```bash
python src\bluetooth_intercom_test.py
```
Use your Realme Buds + any other Bluetooth headset you have (WI-C100, SBH54, etc.)

### Option B: Loopback to same device
Create a test where Realme Buds mic → Realme Buds speaker (hear yourself)

## 🚀 When It Works...

Once you confirm the Bluetooth intercom works, we'll add:
- ✅ GUI interface for easy device selection
- ✅ Push-to-Talk (PTT) button
- ✅ Voice activation (VOX)
- ✅ Audio level meters
- ✅ Battery status display
- ✅ Auto-reconnection

## 📝 Report Back

After testing, let me know:
1. How many Bluetooth devices Windows shows as active?
2. Does the test detect your Realme Buds?
3. What error (if any) do you get?
4. Can you hear audio routing?

Then we'll tackle the specific issues you encounter!
