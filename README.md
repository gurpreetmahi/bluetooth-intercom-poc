# Bluetooth Intercom POC

A proof-of-concept Python application that enables two-way audio communication between two pairs of Bluetooth earbuds (Realme Buds T01) using a PC as a gateway.

## ⚠️ Windows Bluetooth Limitation & Solution

**Windows Bluetooth HFP (Hands-Free Profile) limitation:** One active connection per adapter.

**Your Configuration Status:**
- ✅ You have **2 separate Bluetooth adapters** (verified by diagnostics)
- ✅ Devices are on **different adapters** 
- ✅ Dual-device operation **is possible**

**Current Issue:**
- Devices are paired but not in **active audio state**
- Windows keeps Bluetooth in standby until audio is triggered
- Need to "wake up" devices before PyAudio can stream

**Solutions:**

### Option 1: Use Multiple USB Bluetooth Adapters (BEST) ✅
If you only have one adapter, buy:
- 2x USB Bluetooth dongles (~$10-15 each)
- Recommended: TP-Link UB400, Plugable USB-BT4LE, ASUS USB-BT500
- See [DUAL_ADAPTER_SOLUTION.md](DUAL_ADAPTER_SOLUTION.md) for complete setup guide

**How it works:** Each USB dongle = separate driver instance = separate SCO audio channel

### Option 2: Hybrid Mode (PC + Bluetooth)
- ✅ Works with single Bluetooth adapter
- One person uses PC mic/speakers
- Other person uses Bluetooth earbuds
- Test script: `src/test_pc_audio.py`

### Option 3: Linux PC
- Linux BlueZ stack supports multiple HFP connections natively
- Same Python code should work

### Option 4: ESP32 Gateway (Original Vision)
- ESP32 can handle 2+ simultaneous Bluetooth connections
- Portable, battery-powered
- Requires embedded programming

See [WINDOWS_LIMITATION.md](WINDOWS_LIMITATION.md) for detailed technical explanation.

## Overview

This project demonstrates Bluetooth audio routing. Due to Windows limitations, it currently works as a hybrid system with one Bluetooth device and PC audio.

## Features

- 🎧 Dual Bluetooth earbud connection
- 🎤 Bidirectional audio routing
- 🔘 Push-to-talk (PTT) mode
- 🔊 Always-on intercom mode
- 🖥️ Simple GUI interface
- 📊 Audio level monitoring

## Architecture

```
Person A's Realme Buds ←→ PC Gateway ←→ Person B's Realme Buds
   (mic + speaker)         (audio router)      (mic + speaker)
```

## System Requirements

- **OS**: Windows 10/11 with Bluetooth support
- **Python**: 3.8 or higher
- **Hardware**: 
  - PC with Bluetooth adapter
  - 2x Realme Buds T01 (or compatible Bluetooth earbuds)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/bluetooth-intercom-poc.git
cd bluetooth-intercom-poc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Pair both earbud sets with your PC via Windows Bluetooth settings

## Quick Start

### Prerequisites
- Windows 10/11 with Bluetooth
- Python 3.8+
- 1x Bluetooth earbuds (Realme Buds T01 or any Bluetooth headset)
- Device paired in Windows

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gurpreetmahi/bluetooth-intercom-poc.git
cd bluetooth-intercom-poc
```

2. **Verify dependencies** (Python 3.8+ required):
```bash
python verify_install.py
```

3. **If dependencies are missing**, install them:
```bash
pip install pyaudio numpy pywin32 comtypes PyYAML colorama pytest
```

**Note for Python 3.13 users**: See [INSTALL_PYTHON313.md](INSTALL_PYTHON313.md) for installation tips. System Python is recommended over virtual environments for now.

4. Pair Bluetooth device with your PC (Settings → Bluetooth)

### Step-by-Step Usage

#### Step 0: Check Your Bluetooth Configuration 🔍 NEW!
Run the diagnostic to check if dual-device operation is possible:
```bash
python src/check_bt_config.py
```

**This will tell you:**
- How many Bluetooth adapters you have
- Which devices are on which adapter
- Whether dual-device operation will work
- What hardware you need to buy (if any)

**If diagnostic shows ✅ READY:** Continue to Step 1
**If diagnostic shows ❌ NOT READY:** See [DUAL_ADAPTER_SOLUTION.md](DUAL_ADAPTER_SOLUTION.md)

#### Step 1: Test Basic Audio Routing ✅
Verify the routing logic works with your PC audio:
```bash
python src/test_loopback.py
```
**Expected**: You hear yourself through speakers (5 second test)

#### Step 2: Activate Bluetooth Devices 📡
Devices need to be in active audio state before streaming:
```bash
python src/activate_bt_devices.py
```

**This script will:**
1. Guide you through manually triggering Windows to activate each device
2. Open audio streams to keep devices active
3. Hold streams open for testing

**Keep this terminal window open!**

#### Step 3: Test Dual Bluetooth Intercom (if you have 2 adapters)
In a **NEW terminal window** (keep Step 2 running):
```bash
python src/bluetooth_intercom_test.py
```

**If you only have 1 adapter, use hybrid mode:**
```bash
python src/test_hybrid_intercom.py
```

**What hybrid mode does:**
- Person A uses: PC microphone + speakers
- Person B uses: Bluetooth earbuds
- Routes audio bidirectionally between them

#### Step 4: Understanding the Limitation ⚠️
Read [WINDOWS_LIMITATION.md](WINDOWS_LIMITATION.md) to understand:
- Why dual Bluetooth needs multiple adapters on Windows
- Technical details about `bthmodem.sys` and SCO channels
- Alternative approaches (ESP32, Linux, etc.)

### Quick Reference Card

```bash
# 1. Verify everything is installed
python verify_install.py

# 2. Test basic audio (PC mic/speakers)  
python src/test_loopback.py

# 3. Test hybrid intercom (PC ←→ Bluetooth) - THIS WORKS!
python src/test_hybrid_intercom.py

# 4. Read about Windows limitation
# See WINDOWS_LIMITATION.md for why dual Bluetooth fails
```

### Troubleshooting

**"[Errno -9999] Unanticipated host error"**
- This means device is paired but not active for audio
- Solution 1: Use `python src/activate_and_hold.py` (keeps streams open)
- Solution 2: Manually activate in Windows Settings → System → Sound → click device → Test
- **Important**: Run the intercom test immediately after activation

**"Device NOT available"**
- Windows releases Bluetooth audio devices quickly when idle
- Keep the `activate_and_hold.py` script running in one terminal
- Run the intercom test in a separate terminal window
- Both Realme Buds need to be actively playing audio

**"No Bluetooth devices found"**
- Ensure devices are paired in Windows Bluetooth settings
- Bluetooth must be enabled
- Devices should appear in Sound settings as "Headset" devices
- Check: Settings → Bluetooth & devices

**See [TESTING.md](TESTING.md) for detailed troubleshooting guide**

## Project Structure

```
bluetooth-intercom-poc/
├── src/
│   ├── main.py                   # Main GUI application
│   ├── cli_test.py               # CLI testing tool
│   ├── bluetooth_manager.py      # Bluetooth device management
│   ├── audio_router.py           # Audio routing logic
│   ├── audio_device.py           # Audio device interface
│   └── gui.py                    # GUI components
├── tests/
│   ├── test_bluetooth.py
│   ├── test_audio_router.py
│   └── test_integration.py
├── config.yaml                   # Configuration file
├── requirements.txt              # Python dependencies
├── .gitignore
└── README.md
```

## Development Roadmap

### Phase 1: Core Functionality ✅
- [x] Bluetooth device discovery
- [ ] Single device audio capture
- [ ] Single device audio playback
- [ ] Basic audio routing

### Phase 2: Dual Device Support
- [ ] Connect to two Bluetooth devices simultaneously
- [ ] Bidirectional audio routing
- [ ] Latency optimization

### Phase 3: User Interface
- [ ] CLI testing interface
- [ ] GUI with device selection
- [ ] PTT button implementation
- [ ] Audio level indicators

### Phase 4: Enhancement
- [ ] Voice-activated transmission (VOX)
- [ ] Audio quality improvements
- [ ] Configuration persistence
- [ ] Error handling and recovery

## Known Limitations

- **Latency**: Expect 200-500ms audio delay due to Bluetooth stack
- **Audio Quality**: Limited to HFP profile quality (8kHz mono)
- **Windows Only**: Initial POC targets Windows; Linux/Mac support planned
- **Simultaneous Connections**: Windows Bluetooth stack limitations may affect performance

## Troubleshooting

### Devices won't connect
- Ensure both earbud pairs are paired in Windows Bluetooth settings
- Check that devices are not connected to other devices (phones, etc.)
- Restart Bluetooth service: `net stop bthserv && net start bthserv`

### No audio or choppy audio
- Check audio sample rates match
- Reduce buffer size in config.yaml
- Ensure no other applications are using Bluetooth audio

## Contributing

Contributions welcome! Please open an issue first to discuss proposed changes.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built for Realme Buds T01 intercom project
- Uses PyAudio, pywin32, and comtypes for Windows Bluetooth support

## Contact

Issues and questions: [GitHub Issues](https://github.com/YOUR_USERNAME/bluetooth-intercom-poc/issues)
