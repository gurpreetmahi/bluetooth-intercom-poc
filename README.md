# Bluetooth Intercom POC

A proof-of-concept Python application that enables two-way audio communication between two pairs of Bluetooth earbuds (Realme Buds T01) using a PC as a gateway.

## Overview

This project turns your PC into a Bluetooth audio gateway, routing microphone audio from one pair of earbuds to another, creating an intercom/walkie-talkie system without needing smartphones.

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
- 2x Bluetooth earbuds (Realme Buds T01 or any Bluetooth headsets)
- Both devices paired in Windows

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

4. Pair both Bluetooth devices with your PC (Settings → Bluetooth)

### Step-by-Step Usage

#### Step 1: Test Basic Audio Routing ✅
Verify the routing logic works with your PC audio:
```bash
python src/test_loopback.py
```
**Expected**: You hear yourself through speakers (5 second test)

#### Step 2: Activate Your Bluetooth Devices 🔑
**This is the critical step!** Run the guided activation:
```bash
python src/activate_devices_guide.py
```

This interactive script will:
1. Detect your Bluetooth devices
2. Guide you step-by-step through Windows Settings
3. Test each device to confirm it's active
4. Automatically launch the intercom test

**Follow the on-screen instructions carefully!**

#### Step 3: Bluetooth Intercom Runs Automatically 🎉
If devices are active, the intercom starts:
- Speak into Device A → Hear in Device B
- Speak into Device B → Hear in Device A

### Quick Reference Card

```bash
# 1. Verify everything is installed
python verify_install.py

# 2. Test basic audio (PC mic/speakers)
python src/test_loopback.py

# 3. Follow guided Bluetooth activation
python src/activate_devices_guide.py

# 4. The intercom launches automatically!
```

### Troubleshooting

**"Device NOT available"**
- Run `python src/activate_bluetooth.py` first
- Or manually play audio through each device in Windows Sound settings
- Windows keeps only one Bluetooth device fully active at a time

**"No Bluetooth devices found"**
- Ensure devices are paired in Windows Bluetooth settings
- Bluetooth must be enabled
- Devices should appear in Sound settings

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
