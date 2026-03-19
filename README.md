# autoscroll

Middle-click autoscroll for Linux on Wayland (KDE Plasma).

Replicates the autoscroll behavior found in Windows and Firefox — hold down the middle mouse button and move the mouse to scroll. Move slowly for slow scroll, move fast for fast scroll.

## Why

KDE Plasma on Wayland has no built-in middle-click autoscroll. This daemon runs in the background and adds that functionality system-wide, across all applications.

## How it works

The script listens passively to raw mouse input via `evdev` and injects scroll events through a virtual `uinput` device. It does **not** grab exclusive control of the mouse, so the mouse always works normally — the daemon crashing or stopping will never lock up your mouse.

## Requirements

- Linux with Wayland (tested on KDE Plasma / CachyOS)
- `python-evdev`
- User must be in the `input` group

## Installation

**1. Install dependency**
```bash
sudo pacman -S python-evdev
```

**2. Add yourself to the `input` group**
```bash
sudo usermod -aG input $USER
```
Log out and back in for this to take effect.

**3. Copy the script**
```bash
cp autoscroll.py ~/.local/bin/autoscroll.py
chmod +x ~/.local/bin/autoscroll.py
```

**4. Install the systemd user service**
```bash
mkdir -p ~/.config/systemd/user
cp autoscroll.service ~/.config/systemd/user/autoscroll.service
systemctl --user daemon-reload
systemctl --user enable --now autoscroll.service
```

## Usage

Hold the middle mouse button and move the mouse to scroll. No configuration needed.

## Tuning

In `autoscroll.py`, adjust this value to your preference:

```python
SCROLL_THRESHOLD = 15  # pixels of mouse movement per scroll tick (lower = more sensitive)
```

## Useful commands

```bash
# Check status
systemctl --user status autoscroll

# View logs
journalctl --user -u autoscroll -f

# Stop
systemctl --user stop autoscroll

# Uninstall
systemctl --user disable --now autoscroll
rm ~/.local/bin/autoscroll.py
rm ~/.config/systemd/user/autoscroll.service
```

## Files

| File | Description |
|---|---|
| `autoscroll.py` | The daemon |
| `autoscroll.service` | Systemd user service (auto-start on login) |

## License

MIT
