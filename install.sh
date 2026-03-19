#!/usr/bin/env bash
# install.sh - Installs autoscroll daemon

set -e

echo "=== Autoscroll Installer ==="

# 1. Install python-evdev
echo "→ Installing python-evdev..."
if command -v paru &>/dev/null; then
    paru -S --needed --noconfirm python-evdev
elif command -v pacman &>/dev/null; then
    sudo pacman -S --needed --noconfirm python-evdev
else
    echo "ERROR: pacman not found. Install python-evdev manually."
    exit 1
fi

# 2. Add user to 'input' group (needed for /dev/input access)
echo "→ Adding $USER to 'input' group..."
sudo usermod -aG input "$USER"

# 3. Copy script
echo "→ Installing autoscroll.py to ~/.local/bin/"
mkdir -p "$HOME/.local/bin"
cp autoscroll.py "$HOME/.local/bin/autoscroll.py"
chmod +x "$HOME/.local/bin/autoscroll.py"

# 4. Install systemd user service
echo "→ Installing systemd user service..."
mkdir -p "$HOME/.config/systemd/user"
cp autoscroll.service "$HOME/.config/systemd/user/autoscroll.service"
systemctl --user daemon-reload
systemctl --user enable --now autoscroll.service

echo ""
echo "✓ Done! Autoscroll is installed and running."
echo ""
echo "NOTE: You need to log out and back in for the 'input' group to take effect."
echo "      After that the service will start automatically on login."
echo ""
echo "Useful commands:"
echo "  systemctl --user status autoscroll    # check status"
echo "  systemctl --user restart autoscroll   # restart"
echo "  systemctl --user disable autoscroll   # disable autostart"
echo "  journalctl --user -u autoscroll -f    # live log"
