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

## Usage

### Command Line Mode (Testing)
```bash
python src/cli_test.py
```

### GUI Mode
```bash
python src/main.py
```

### Configuration

Edit `config.yaml` to customize:
- Audio buffer sizes
- Sample rates
- PTT key bindings
- Device names

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
