# Razer DPI OSD

A lightweight on-screen display for Razer mice on Linux that shows a popup when you change DPI with the mouse button — similar to Razer Synapse on Windows.

![PyQt6](https://img.shields.io/badge/PyQt6-grey?logo=qt) ![OpenRazer](https://img.shields.io/badge/OpenRazer-green) ![Linux](https://img.shields.io/badge/Linux-grey?logo=linux&logoColor=white)

## Features

- Detects DPI changes in real time via sysfs polling
- Modern translucent popup with DPI value, progress bar, and stage indicators
- Fade in/out animations
- Click-through — doesn't steal focus or block input
- System tray icon
- Works with any Razer mouse supported by OpenRazer

## Requirements

- Linux (X11 or Wayland)
- [OpenRazer](https://openrazer.github.io/) daemon and driver installed
- Python 3.10+
- PyQt6
- python-xlib (for X11 click-through)

## Installation

```bash
git clone https://github.com/jolinarn/razer-dpi-osd.git
cd razer-dpi-osd
```

Make sure OpenRazer is installed and the daemon is running:

```bash
# Arch / CachyOS
sudo pacman -S openrazer-daemon openrazer-driver-dkms python-openrazer

# Ubuntu / Debian
sudo apt install openrazer-meta
```

## Usage

```bash
cd ~/razer-dpi-osd
python3 -m razer_dpi_osd
```

Press the DPI button on your mouse and the OSD will appear.

### Autostart (KDE / GNOME)

Copy the desktop entry to autostart:

```bash
cp ~/.config/autostart/razer-dpi-osd.desktop ~/.config/autostart/
```

Or create one:

```ini
[Desktop Entry]
Type=Application
Name=Razer DPI OSD
Exec=bash -c "cd ~/razer-dpi-osd && python3 -m razer_dpi_osd"
Icon=input-mouse
X-GNOME-Autostart-enabled=true
```

## License

MIT
