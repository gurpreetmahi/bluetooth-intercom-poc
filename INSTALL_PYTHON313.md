# Installation Guide for Python 3.13

## The Problem
PyAudio 0.2.14 doesn't have pre-built wheels for Python 3.13 yet, causing installation failures in virtual environments.

## ✅ Simple Solution: Use System Python

Your system Python already has all required packages installed. Simply don't use the virtual environment:

### Verify System Installation
```bash
python --version  # Should show Python 3.13.7
python -c "import pyaudio; print('PyAudio OK')"
python -c "import numpy; print('NumPy OK')"
python -c "import win32com.client; print('pywin32 OK')"
```

### Run the Project (Without Virtual Environment)
```bash
cd c:\Users\gurpr\source\github\bluetooth-intercom-poc

# Just use python directly (not the .venv)
python src\test_loopback.py
python src\bluetooth_intercom_test.py
```

## Alternative: Fix Virtual Environment (Advanced)

If you really need a virtual environment:

### Option 1: Use PyAudio from GitHub (Python 3.13 compatible)
```bash
pip install --upgrade pip setuptools wheel
pip install git+https://github.com/intxcc/pyaudio_portaudio.git
```

### Option 2: Use pipwin (Windows package manager)
```bash
pip install pipwin
pipwin install pyaudio
```

### Option 3: Download Pre-built Wheel
1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Download: `PyAudio‑0.2.14‑cp313‑cp313‑win_amd64.whl` (if available)
3. Install: `pip install PyAudio‑0.2.14‑cp313‑cp313‑win_amd64.whl`

### Option 4: Rebuild from Source (Requires Visual Studio)
```bash
# Install Visual Studio Build Tools first
pip install --upgrade pip setuptools wheel
pip install pyaudio --no-binary :all:
```

## 💡 Recommended Approach

**Just use system Python!** Your system already has everything working:
- ✅ PyAudio installed
- ✅ NumPy installed  
- ✅ pywin32 installed
- ✅ All other dependencies

Simply run scripts with `python` command (not in .venv).

## Verification Script

Run this to verify everything works:
```bash
python -c "import pyaudio, numpy, win32com.client, yaml, colorama; print('✅ All packages OK!')"
```

If you see `✅ All packages OK!`, you're ready to go!

## For Future Projects

When Python 3.13 support improves (a few months), PyAudio wheels will be available. Until then:
- Use system Python for this project
- OR use Python 3.11 or 3.12 for virtual environments
