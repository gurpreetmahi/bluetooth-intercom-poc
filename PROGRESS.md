# Bluetooth Intercom POC - Progress Summary

## ✅ Completed (Session 1)

### Project Setup
- ✅ Created complete Python project structure
- ✅ Initialized Git repository
- ✅ Created GitHub repository: https://github.com/gurpreetmahi/bluetooth-intercom-poc
- ✅ Created 11 GitHub issues for development roadmap
- ✅ Installed all dependencies (PyAudio, NumPy, pywin32, etc.)

### Core Functionality
- ✅ **Bluetooth Device Detection**: Successfully detecting 3 Bluetooth headsets:
  - Talk Three (indices: input=11, output=10)
  - WI-C100 (indices: input=24, output=23)
  - SBH54 (indices: input=27, output=26)
  
- ✅ **Audio Device Enumeration**: `list_audio_devices()` successfully lists all 28 audio devices
- ✅ **Device Pairing Logic**: Correctly pairs input/output streams for each Bluetooth device
- ✅ **Simple POC Script**: Created `simple_poc.py` that demonstrates the concept

### Code Architecture
- ✅ `bluetooth_manager.py` - Device discovery and management
- ✅ `audio_router.py` - Audio stream routing logic
- ✅ `gui.py` - Tkinter GUI framework
- ✅ `cli_test.py` - Command-line testing utility
- ✅ `simple_poc.py` - Minimal working proof of concept

## 🔄 Current Status

### Key Finding
The Bluetooth devices are **paired but not actively connected** for audio streaming. This causes PyAudio error `-9999 Unanticipated host error` when trying to open audio streams.

### What This Means
1. **Devices appear in Windows**: All 3 Bluetooth headsets show up in audio device list
2. **Not actively streaming**: Devices need to be in active audio connection state
3. **Windows limitation**: Windows typically only maintains active audio connection to one Bluetooth device at a time

## 🎯 Next Steps

### Immediate Actions (High Priority)

**1. Test with Real Devices** 🔴
- **Action**: Ensure both Realme Buds T01 pairs are actively connected
- **How**: Play audio to each device in Windows to establish active connection
- **Test**: Run `python src\simple_poc.py` when both devices show audio activity

**2. Handle Device States**
- Add connection state checking before opening streams
- Implement "activate" function to trigger Windows to connect audio
- Add retry logic for device connection

**3. Single Device Test**
- Simplify to test with one Bluetooth device first (loopback test)
- Record from mic → Play back to same device speaker
- Verify basic audio routing works

### Alternative Approaches

**Option A: Auto-Activate Devices**
- Research Windows APIs to programmatically activate Bluetooth audio
- Use `IMMDevice` and `IMMDeviceEnumerator` COM interfaces
- Trigger connection before opening PyAudio streams

**Option B: Manual Connection Requirement**
- Document that users must manually initiate audio to both devices
- Provide clear instructions in README
- Check device state before attempting to route

**Option C: Use Virtual Audio Cables**
- Install VB-Audio Cable or similar
- Route Bluetooth → Virtual Cable → Other Bluetooth
- More reliable but requires additional software

## 📝 Technical Notes

### Bluetooth Profile Details
- **Profile**: HFP (Hands-Free Profile)
- **Sample Rate**: 8000 Hz (phone call quality)
- **Channels**: Mono (1 channel)
- **Format**: 16-bit PCM

### Windows Bluetooth Limitations
1. Windows typically maintains one active HFP connection at a time
2. Multiple devices can be paired but not simultaneously active
3. A2DP (high quality) profile has similar limitations
4. Enterprise Bluetooth adapters may support multiple simultaneous connections

### Expected Latency
- Bluetooth HFP: ~100-150ms inherent latency
- Audio buffering: ~50-100ms
- Processing overhead: ~20-50ms
- **Total estimated: 200-400ms** (walkie-talkie feel)

## 🔧 Known Issues

1. **Issue**: PyAudio error -9999 when opening Bluetooth streams
   - **Cause**: Devices not in active audio state
   - **Status**: Investigating activation methods

2. **Issue**: Only one Bluetooth device can be fully active at a time
   - **Cause**: Windows Bluetooth stack limitation
   - **Status**: Researching workarounds

## 📊 Test Results

### CLI Test Utility
```bash
python src/cli_test.py
```
- ✅ Successfully lists all audio devices
- ✅ Detects 3 Bluetooth headsets
- ✅ Shows device capabilities (input/output channels, sample rates)

### Simple POC
```bash
python src/simple_poc.py  
```
- ✅ Correctly identifies 3 complete Bluetooth devices
- ✅ Auto-selects first two devices for routing
- ❌ Fails to open audio streams (devices not active)

## 🎓 Lessons Learned

1. **Device Detection ≠ Active Connection**: Paired Bluetooth devices appear in PyAudio list but aren't necessarily ready for streaming

2. **Windows Bluetooth is Limiting**: Unlike some Linux distributions, Windows doesn't easily support multiple simultaneous HFP audio connections

3. **PyAudio Error Codes**: Error -9999 is generic "host error" - usually device unavailable or in use

4. **Better Testing Approach**: Should test with regular PC audio devices first (microphone + speakers) to verify routing logic, then move to Bluetooth

## 📚 Resources

- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/)
- [Windows Core Audio APIs](https://docs.microsoft.com/en-us/windows/win32/coreaudio/core-audio-apis)
- [Bluetooth HFP Specification](https://www.bluetooth.com/specifications/specs/hands-free-profile-1-8/)

## 🚀 Quick Start for Contributors

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Test device detection: `python src/cli_test.py` → Option 2
4. View Bluetooth devices: Check for "Headset" entries with `bthhfenum`
5. Run simple POC: `python src/simple_poc.py`

## 💡 Recommendations

**For Immediate Testing:**
1. Test audio routing with regular PC audio devices first (not Bluetooth)
2. Verify routing logic works with standard microphone → speakers
3. Then tackle Bluetooth-specific challenges

**For Production:**
1. Implement device state monitoring
2. Add auto-activation if possible
3. Provide clear user instructions for manual activation
4. Add fallback to indicate when devices are unavailable

---

**Last Updated**: March 15, 2026  
**Status**: Initial POC completed, device activation challenges identified  
**Next Session**: Focus on device activation and test with active Bluetooth connections
