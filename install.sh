#!/bin/bash
# SocialSync — Desktop Launcher Installer
# Adds SocialSync to your application menu (GNOME, KDE, XFCE, etc.)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/socialsync.py"

echo "⬡ SocialSync Installer"
echo "----------------------"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 not found. Install it with: sudo apt install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION found"

# Check/install pip
if ! command -v pip3 &>/dev/null; then
    echo "Installing pip3..."
    sudo apt install -y python3-pip
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install PyQt6 requests Pillow --break-system-packages

echo "✓ Dependencies installed"

# Create desktop entry
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/socialsync.desktop" << EOF
[Desktop Entry]
Name=SocialSync
GenericName=Social Media Cross-Poster
Comment=Cross-post photos to Mastodon, Pixelfed, Bluesky, and Threads
Exec=python3 $APP_PATH
Icon=applications-multimedia
Terminal=false
Type=Application
Categories=Network;Social;FileTransfer;
Keywords=mastodon;pixelfed;bluesky;threads;social;photo;post;
StartupWMClass=socialsync
EOF

chmod +x "$DESKTOP_DIR/socialsync.desktop"

# Update desktop database if available
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "✓ Desktop launcher created"
echo ""
echo "✅ Installation complete!"
echo ""
echo "  Run from terminal:  python3 $APP_PATH"
echo "  Or search 'SocialSync' in your application menu"
