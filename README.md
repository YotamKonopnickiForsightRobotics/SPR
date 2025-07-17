# SPR Log Collector

**SPR** is a GUI-based tool that connects to a remote machne over SSH, zips relevant runtime logs and data, and downloads the result to your local machine.
A description entered by the user is appended to the zip file. Ideal for diagnostics and offline analysis.

---

## ✅ Features

- Simple Tkinter GUI for user description
- Automatic SSH connection to a remote machine
- Collects recent `.pcap` files, logs, and directories
- Compresses all files remotely and copies them to local machine
- Adds a description file into the zip
- Visual progress window during the operation

---

## 📦 Getting Started

### 🔸 Option 1: Use the Precompiled `.exe` (Windows only)

1. Download the latest `SPR.exe` from the [Releases](#) page or repository root.
2. Double-click `SPR.exe` to run it.
3. A GUI window will prompt for a description. Enter and submit.
4. A progress bar will appear. Once finished, you will see `SPR.zip` in the same directory.

> ⚠ Make sure your firewall/antivirus allows outgoing SSH on port 22.

---

### 🔸 Option 2: Run from Python Source (Cross-platform)

#### Requirements

- Python 3.7+
- `paramiko` for SSH
- No external GUI libraries required (uses built-in `tkinter`)

#### Installation

```bash
pip install paramiko
