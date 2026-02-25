#!/usr/bin/env python3
"""
SocialSync - Cross-platform social media photo poster
Supports: Mastodon, Pixelfed, Bluesky, Threads
"""

import sys
import os
import json
import base64
import mimetypes
import threading
from pathlib import Path
from datetime import datetime, timezone

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QCheckBox, QScrollArea,
    QFrame, QFileDialog, QTabWidget, QMessageBox, QProgressBar,
    QStackedWidget, QSplitter, QGroupBox, QSpinBox, QComboBox,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QGridLayout, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QTimer, QPropertyAnimation,
    QEasingCurve, QRect
)
from PyQt6.QtGui import (
    QPixmap, QFont, QIcon, QPalette, QColor, QImage, QPainter,
    QLinearGradient, QBrush, QPen, QFontDatabase, QCursor
)

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

CONFIG_FILE = Path.home() / ".config" / "socialsync" / "config.json"

# ─── Stylesheet ──────────────────────────────────────────────────────────────

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: 'Inter', 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 14px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

QScrollBar:vertical {
    background: #1a1f2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #3a4060;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QPushButton {
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #7c7ff5;
}
QPushButton:pressed {
    background-color: #4f52d4;
}
QPushButton:disabled {
    background-color: #2a2f42;
    color: #555b7a;
}

QPushButton.secondary {
    background-color: #1e2337;
    color: #a0aec0;
    border: 1px solid #2d3555;
}
QPushButton.secondary:hover {
    background-color: #252a40;
    color: #e2e8f0;
}

QPushButton.danger {
    background-color: #ef4444;
}
QPushButton.danger:hover {
    background-color: #f87171;
}

QPushButton.success {
    background-color: #10b981;
}
QPushButton.success:hover {
    background-color: #34d399;
}

QTextEdit, QLineEdit {
    background-color: #1a1f2e;
    color: #e2e8f0;
    border: 1px solid #2d3555;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: #6366f1;
}
QTextEdit:focus, QLineEdit:focus {
    border: 1px solid #6366f1;
}

QTabWidget::pane {
    border: 1px solid #2d3555;
    border-radius: 12px;
    background: #141824;
    top: -1px;
}
QTabBar::tab {
    background: #1a1f2e;
    color: #718096;
    padding: 10px 22px;
    border-radius: 8px 8px 0 0;
    margin-right: 4px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: #141824;
    color: #e2e8f0;
    border-bottom: 2px solid #6366f1;
}
QTabBar::tab:hover {
    color: #e2e8f0;
    background: #1e2337;
}

QCheckBox {
    color: #a0aec0;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid #3a4060;
    background: #1a1f2e;
}
QCheckBox::indicator:checked {
    background: #6366f1;
    border-color: #6366f1;
    image: url(none);
}
QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QLabel {
    color: #e2e8f0;
}

QLabel.title {
    font-size: 22px;
    font-weight: 700;
    color: #f8fafc;
}
QLabel.subtitle {
    font-size: 13px;
    color: #718096;
}
QLabel.section {
    font-size: 12px;
    font-weight: 600;
    color: #6366f1;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QLabel.status-ok {
    color: #10b981;
    font-size: 12px;
}
QLabel.status-error {
    color: #ef4444;
    font-size: 12px;
}

QProgressBar {
    background: #1a1f2e;
    border-radius: 6px;
    height: 8px;
    border: none;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #a855f7);
    border-radius: 6px;
}

QSplitter::handle {
    background: #2d3555;
    width: 1px;
}

QGroupBox {
    border: 1px solid #2d3555;
    border-radius: 12px;
    margin-top: 20px;
    padding: 14px;
    color: #a0aec0;
    font-size: 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 14px;
    color: #6366f1;
}

QComboBox {
    background: #1a1f2e;
    border: 1px solid #2d3555;
    border-radius: 8px;
    padding: 6px 12px;
    color: #e2e8f0;
    min-width: 120px;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background: #1a1f2e;
    border: 1px solid #3a4060;
    border-radius: 8px;
    color: #e2e8f0;
    selection-background-color: #6366f1;
}

QFrame.card {
    background: #141824;
    border: 1px solid #2d3555;
    border-radius: 14px;
    padding: 0px;
}

QFrame.platform-card {
    background: #1a1f2e;
    border: 1px solid #2d3555;
    border-radius: 12px;
}

QFrame.preview-card {
    background: #141824;
    border: 1px solid #2d3555;
    border-radius: 16px;
}
"""

# ─── Platform configs ─────────────────────────────────────────────────────────

PLATFORMS = {
    "mastodon": {
        "label": "Mastodon",
        "color": "#6364ff",
        "icon": "🐘",
        "char_limit": 500,
    },
    "pixelfed": {
        "label": "Pixelfed",
        "color": "#ff5c5c",
        "icon": "📸",
        "char_limit": 2200,
    },
    "bluesky": {
        "label": "Bluesky",
        "color": "#0085ff",
        "icon": "🦋",
        "char_limit": 300,
    },
    "threads": {
        "label": "Threads",
        "color": "#101010",
        "icon": "@",
        "char_limit": 500,
    },
}

# ─── Config Manager ───────────────────────────────────────────────────────────

class ConfigManager:
    def __init__(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self):
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                pass
        return {
            "accounts": [],
            "last_post": {},
        }

    def save(self):
        CONFIG_FILE.write_text(json.dumps(self.data, indent=2))

    def get_accounts(self):
        return self.data.get("accounts", [])

    def add_account(self, account):
        accounts = self.data.setdefault("accounts", [])
        # Replace if same platform+username
        for i, a in enumerate(accounts):
            if a["platform"] == account["platform"] and a["username"] == account["username"]:
                accounts[i] = account
                self.save()
                return
        accounts.append(account)
        self.save()

    def remove_account(self, idx):
        self.data["accounts"].pop(idx)
        self.save()


# ─── Posting Worker ───────────────────────────────────────────────────────────

class PostWorker(QThread):
    progress = pyqtSignal(str, str)   # platform_key, status message
    done = pyqtSignal(dict)           # results dict

    def __init__(self, accounts, text, image_path, alt_text=""):
        super().__init__()
        self.accounts = accounts
        self.text = text
        self.image_path = image_path
        self.alt_text = alt_text

    def run(self):
        results = {}
        for account in self.accounts:
            platform = account["platform"]
            key = f"{platform}:{account['username']}"
            try:
                self.progress.emit(key, "Uploading…")
                result = self._post(account)
                results[key] = {"ok": True, "url": result}
                self.progress.emit(key, "✓ Posted!")
            except Exception as e:
                results[key] = {"ok": False, "error": str(e)}
                self.progress.emit(key, f"✗ {str(e)[:60]}")
        self.done.emit(results)

    def _post(self, account):
        platform = account["platform"]
        if platform == "mastodon":
            return self._post_mastodon(account)
        elif platform == "pixelfed":
            return self._post_pixelfed(account)
        elif platform == "bluesky":
            return self._post_bluesky(account)
        elif platform == "threads":
            return self._post_threads(account)
        else:
            raise ValueError(f"Unknown platform: {platform}")

    def _post_mastodon(self, account):
        base = account["instance"].rstrip("/")
        token = account["token"]
        headers = {"Authorization": f"Bearer {token}"}

        media_id = None
        if self.image_path:
            with open(self.image_path, "rb") as f:
                mime = mimetypes.guess_type(self.image_path)[0] or "image/jpeg"
                r = requests.post(
                    f"{base}/api/v2/media",
                    headers=headers,
                    files={"file": (os.path.basename(self.image_path), f, mime)},
                    data={"description": self.alt_text},
                    timeout=60
                )
                r.raise_for_status()
                media_id = r.json()["id"]

        payload = {"status": self.text}
        if media_id:
            payload["media_ids[]"] = media_id

        r = requests.post(f"{base}/api/v1/statuses", headers=headers, data=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("url", "")

    def _post_pixelfed(self, account):
        # Pixelfed uses Mastodon-compatible API
        base = account.get("instance", "https://pixelfed.social").rstrip("/")
        token = account["token"]
        headers = {"Authorization": f"Bearer {token}"}

        media_id = None
        if self.image_path:
            with open(self.image_path, "rb") as f:
                mime = mimetypes.guess_type(self.image_path)[0] or "image/jpeg"
                r = requests.post(
                    f"{base}/api/v1/media",
                    headers=headers,
                    files={"file": (os.path.basename(self.image_path), f, mime)},
                    data={"description": self.alt_text},
                    timeout=60
                )
                r.raise_for_status()
                media_id = r.json()["id"]

        payload = {"status": self.text}
        if media_id:
            payload["media_ids[]"] = media_id

        r = requests.post(f"{base}/api/v1/statuses", headers=headers, data=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("url", "")

    def _post_bluesky(self, account):
        handle = account["username"]
        password = account["token"]  # app password

        # Auth
        r = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": password},
            timeout=30
        )
        r.raise_for_status()
        session = r.json()
        did = session["did"]
        access_token = session["accessJwt"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Upload image
        blob = None
        if self.image_path:
            with open(self.image_path, "rb") as f:
                img_data = f.read()
            mime = mimetypes.guess_type(self.image_path)[0] or "image/jpeg"
            r = requests.post(
                "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
                headers={**headers, "Content-Type": mime},
                data=img_data,
                timeout=60
            )
            r.raise_for_status()
            blob = r.json()["blob"]

        # Create post
        post = {
            "$type": "app.bsky.feed.post",
            "text": self.text[:300],
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "langs": ["en"],
        }
        if blob:
            post["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": [{
                    "image": blob,
                    "alt": self.alt_text or "",
                }]
            }

        r = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers=headers,
            json={
                "repo": did,
                "collection": "app.bsky.feed.post",
                "record": post,
            },
            timeout=30
        )
        r.raise_for_status()
        uri = r.json().get("uri", "")
        rkey = uri.split("/")[-1] if uri else ""
        return f"https://bsky.app/profile/{handle}/post/{rkey}"

    def _post_threads(self, account):
        user_id = account.get("user_id", "")
        token = account["token"]

        # Step 1: create media container
        payload = {
            "media_type": "IMAGE" if self.image_path else "TEXT",
            "text": self.text[:500],
            "access_token": token,
        }
        if self.image_path:
            # Threads requires a public URL for images - note this limitation
            img_url = account.get("image_url_override", "")
            if not img_url:
                raise ValueError(
                    "Threads requires a public image URL. "
                    "Please host your image and add the URL in account settings."
                )
            payload["image_url"] = img_url

        r = requests.post(
            f"https://graph.threads.net/v1.0/{user_id}/threads",
            data=payload, timeout=30
        )
        r.raise_for_status()
        creation_id = r.json()["id"]

        # Step 2: publish
        r = requests.post(
            f"https://graph.threads.net/v1.0/{user_id}/threads_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=30
        )
        r.raise_for_status()
        post_id = r.json()["id"]
        return f"https://www.threads.net/t/{post_id}"


# ─── Account Dialog ───────────────────────────────────────────────────────────

class AddAccountDialog(QDialog):
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.setWindowTitle("Add Account")
        self.setMinimumWidth(480)
        self.setStyleSheet(DARK_THEME)
        self.result_account = None
        self._build(account)

    def _build(self, account=None):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Add Account")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;")
        layout.addWidget(title)

        # Platform selector
        plat_label = QLabel("Platform")
        plat_label.setStyleSheet("color: #718096; font-size: 12px; font-weight: 600;")
        layout.addWidget(plat_label)

        self.platform_combo = QComboBox()
        for k, v in PLATFORMS.items():
            self.platform_combo.addItem(f"{v['icon']}  {v['label']}", k)
        self.platform_combo.currentIndexChanged.connect(self._update_fields)
        layout.addWidget(self.platform_combo)

        # Dynamic fields container
        self.fields_widget = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_widget)
        self.fields_layout.setSpacing(10)
        self.fields_layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.fields_widget)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.setStyleSheet("background: #1e2337; color: #a0aec0; border: 1px solid #2d3555;")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Add Account")
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        self._update_fields()

        if account:
            # Pre-fill
            idx = self.platform_combo.findData(account["platform"])
            if idx >= 0:
                self.platform_combo.setCurrentIndex(idx)
            self._update_fields()
            for key, widget in self.field_widgets.items():
                if key in account:
                    widget.setText(account[key])

    def _update_fields(self):
        # Clear
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.field_widgets = {}
        platform = self.platform_combo.currentData()

        def add_field(key, label, placeholder="", password=False, hint=None):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #718096; font-size: 12px; font-weight: 600; margin-top: 4px;")
            self.fields_layout.addWidget(lbl)
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            if password:
                inp.setEchoMode(QLineEdit.EchoMode.Password)
            self.fields_layout.addWidget(inp)
            self.field_widgets[key] = inp
            if hint:
                hint_lbl = QLabel(hint)
                hint_lbl.setStyleSheet("color: #4a5568; font-size: 11px;")
                hint_lbl.setWordWrap(True)
                self.fields_layout.addWidget(hint_lbl)

        add_field("username", "Username / Handle", "@you@mastodon.social")

        if platform == "mastodon":
            add_field("instance", "Instance URL", "https://mastodon.social",
                      hint="Your Mastodon server URL")
            add_field("token", "Access Token", "Paste your access token",
                      password=True,
                      hint="Settings → Development → New Application → read+write+follow+push")

        elif platform == "pixelfed":
            add_field("instance", "Instance URL", "https://pixelfed.social",
                      hint="Your Pixelfed instance (default: pixelfed.social)")
            add_field("token", "Access Token", "Paste your access token",
                      password=True,
                      hint="Settings → Applications → New Application")

        elif platform == "bluesky":
            add_field("token", "App Password", "xxxx-xxxx-xxxx-xxxx",
                      password=True,
                      hint="Settings → Privacy and Security → App Passwords")

        elif platform == "threads":
            add_field("user_id", "Threads User ID", "1234567890",
                      hint="Found in Meta Developer Console")
            add_field("token", "Access Token", "Paste long-lived token",
                      password=True,
                      hint="Use Meta Graph API to get a long-lived token")
            add_field("image_url_override", "Public Image URL (optional)",
                      "https://yourserver.com/image.jpg",
                      hint="Threads requires a publicly accessible image URL. Leave blank for text-only.")

    def _save(self):
        platform = self.platform_combo.currentData()
        account = {"platform": platform}
        for key, widget in self.field_widgets.items():
            account[key] = widget.text().strip()

        if not account.get("username"):
            QMessageBox.warning(self, "Missing Field", "Username is required.")
            return
        if not account.get("token"):
            QMessageBox.warning(self, "Missing Field", "Token / Password is required.")
            return

        self.result_account = account
        self.accept()


# ─── Preview Widget ───────────────────────────────────────────────────────────

class SocialPostPreview(QFrame):
    """Renders a mock social media post preview"""

    def __init__(self, platform_key="mastodon", parent=None):
        super().__init__(parent)
        self.platform_key = platform_key
        self.setObjectName("previewCard")
        self._image_pixmap = None
        self._text = ""
        self._username = "@you@mastodon.social"
        self._build()

    def _build(self):
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Card
        card = QFrame()
        card.setObjectName("innerCard")
        p = PLATFORMS.get(self.platform_key, PLATFORMS["mastodon"])
        card.setStyleSheet(f"""
            QFrame#innerCard {{
                background: #1a1f2e;
                border: 1px solid #2d3555;
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(16, 16, 16, 16)

        # Platform badge
        badge_row = QHBoxLayout()
        icon_lbl = QLabel(p["icon"])
        icon_lbl.setStyleSheet(f"font-size: 18px;")
        badge_lbl = QLabel(p["label"])
        badge_lbl.setStyleSheet(f"color: {p['color']}; font-weight: 700; font-size: 13px;")
        badge_row.addWidget(icon_lbl)
        badge_row.addWidget(badge_lbl)
        badge_row.addStretch()
        card_layout.addLayout(badge_row)

        # Profile row
        prof_row = QHBoxLayout()
        avatar = QLabel()
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {p['color']}, stop:1 #a855f7);
            border-radius: 20px;
            color: white; font-weight: 700; font-size: 16px;
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setText("Y")

        prof_info = QVBoxLayout()
        self.display_name = QLabel("You")
        self.display_name.setStyleSheet("font-weight: 700; color: #f8fafc; font-size: 14px;")
        self.handle_label = QLabel(self._username)
        self.handle_label.setStyleSheet("color: #718096; font-size: 12px;")
        prof_info.addWidget(self.display_name)
        prof_info.addWidget(self.handle_label)

        prof_row.addWidget(avatar)
        prof_row.addLayout(prof_info)
        prof_row.addStretch()
        card_layout.addLayout(prof_row)

        # Text preview
        self.text_label = QLabel("Your caption will appear here…")
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("color: #e2e8f0; font-size: 14px; line-height: 1.5;")
        self.text_label.setMinimumHeight(50)
        card_layout.addWidget(self.text_label)

        # Image preview
        self.image_container = QLabel()
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_container.setMinimumHeight(180)
        self.image_container.setMaximumHeight(320)
        self.image_container.setStyleSheet("""
            background: #0f1117;
            border-radius: 10px;
            color: #4a5568;
            font-size: 13px;
        """)
        self.image_container.setText("No image selected")
        card_layout.addWidget(self.image_container)

        # Footer
        footer = QLabel("Just now  ·  Web")
        footer.setStyleSheet("color: #4a5568; font-size: 11px;")
        card_layout.addWidget(footer)

        layout.addWidget(card)

    def set_text(self, text):
        self._text = text
        limit = PLATFORMS.get(self.platform_key, {}).get("char_limit", 500)
        display = text[:limit] if text else "Your caption will appear here…"
        self.text_label.setText(display or "Your caption will appear here…")

    def set_image(self, pixmap):
        self._image_pixmap = pixmap
        if pixmap:
            scaled = pixmap.scaled(
                self.image_container.width() or 400,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_container.setPixmap(scaled)
            self.image_container.setText("")
        else:
            self.image_container.setPixmap(QPixmap())
            self.image_container.setText("No image selected")

    def set_username(self, username):
        self._username = username
        self.handle_label.setText(username)

    def set_platform(self, platform_key):
        self.platform_key = platform_key


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.image_path = None
        self.image_pixmap = None
        self.post_workers = {}

        self.setWindowTitle("SocialSync")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 820)
        self.setStyleSheet(DARK_THEME)

        self._build_ui()
        self._refresh_accounts()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Main content (stacked pages)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_compose_page())   # 0
        self.stack.addWidget(self._build_accounts_page())  # 1
        root.addWidget(self.stack, 1)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background: #0a0d14;
                border-right: 1px solid #1e2337;
            }
        """)
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 24, 16, 24)

        # Logo
        logo = QLabel("⬡ SocialSync")
        logo.setStyleSheet("font-size: 18px; font-weight: 800; color: #6366f1; margin-bottom: 24px;")
        layout.addWidget(logo)

        self.nav_buttons = []

        def nav_btn(icon, label, page_idx):
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #718096;
                    text-align: left;
                    padding: 8px 14px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 500;
                    border: none;
                }
                QPushButton:hover {
                    background: #1a1f2e;
                    color: #e2e8f0;
                }
                QPushButton:checked {
                    background: #1e2047;
                    color: #818cf8;
                    font-weight: 600;
                }
            """)
            btn.clicked.connect(lambda: self._nav(page_idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_btn("✍️", "Compose", 0)
        nav_btn("👤", "Accounts", 1)

        self.nav_buttons[0].setChecked(True)

        layout.addStretch()

        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #2d3555; font-size: 11px;")
        layout.addWidget(version)

        return sidebar

    def _nav(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)

    # ── Compose Page ──────────────────────────────────────────────────────────

    def _build_compose_page(self):
        page = QWidget()
        page.setStyleSheet("background: #0f1117;")
        main_layout = QHBoxLayout(page)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left: compose panel
        compose_panel = QWidget()
        compose_panel.setMaximumWidth(560)
        compose_panel.setMinimumWidth(420)
        cl = QVBoxLayout(compose_panel)
        cl.setSpacing(16)
        cl.setContentsMargins(28, 28, 20, 28)

        # Header
        header = QHBoxLayout()
        title = QLabel("New Post")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #f8fafc;")
        header.addWidget(title)
        header.addStretch()
        cl.addLayout(header)

        # Image drop zone
        self.image_zone = self._build_image_zone()
        cl.addWidget(self.image_zone)

        # Caption
        cap_label = QLabel("CAPTION")
        cap_label.setStyleSheet("color: #4a5568; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        cl.addWidget(cap_label)

        self.caption_edit = QTextEdit()
        self.caption_edit.setPlaceholderText("Write your caption here…")
        self.caption_edit.setMinimumHeight(120)
        self.caption_edit.setMaximumHeight(180)
        self.caption_edit.textChanged.connect(self._on_text_changed)
        cl.addWidget(self.caption_edit)

        # Char counter row
        char_row = QHBoxLayout()
        self.char_counter = QLabel("0 / 500")
        self.char_counter.setStyleSheet("color: #4a5568; font-size: 12px;")
        char_row.addStretch()
        char_row.addWidget(self.char_counter)
        cl.addLayout(char_row)

        # Alt text
        alt_label = QLabel("ALT TEXT (for accessibility)")
        alt_label.setStyleSheet("color: #4a5568; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        cl.addWidget(alt_label)
        self.alt_edit = QLineEdit()
        self.alt_edit.setPlaceholderText("Describe your image for screen readers…")
        cl.addWidget(self.alt_edit)

        # Platform selector
        plat_label = QLabel("POST TO")
        plat_label.setStyleSheet("color: #4a5568; font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-top: 4px;")
        cl.addWidget(plat_label)

        self.accounts_scroll = QScrollArea()
        self.accounts_scroll.setWidgetResizable(True)
        self.accounts_scroll.setMaximumHeight(180)
        self.accounts_scroll.setStyleSheet("border: 1px solid #2d3555; border-radius: 10px; background: #141824;")
        self.accounts_list_widget = QWidget()
        self.accounts_list_layout = QVBoxLayout(self.accounts_list_widget)
        self.accounts_list_layout.setSpacing(6)
        self.accounts_list_layout.setContentsMargins(10, 10, 10, 10)
        self.accounts_scroll.setWidget(self.accounts_list_widget)
        cl.addWidget(self.accounts_scroll)

        # Post button
        self.post_btn = QPushButton("🚀  Post to Selected Platforms")
        self.post_btn.setFixedHeight(50)
        self.post_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #6366f1, stop:1 #a855f7);
                color: white;
                border-radius: 14px;
                font-size: 15px;
                font-weight: 700;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7c7ff5, stop:1 #b468f7);
            }
            QPushButton:disabled {
                background: #1e2337;
                color: #3a4060;
            }
        """)
        self.post_btn.clicked.connect(self._post)
        cl.addWidget(self.post_btn)

        # Progress area
        self.progress_area = QWidget()
        prog_layout = QVBoxLayout(self.progress_area)
        prog_layout.setSpacing(6)
        prog_layout.setContentsMargins(0,0,0,0)
        self.progress_area.setVisible(False)
        cl.addWidget(self.progress_area)

        cl.addStretch()

        main_layout.addWidget(compose_panel)

        # Right: preview panel
        preview_panel = self._build_preview_panel()
        main_layout.addWidget(preview_panel, 1)

        return page

    def _build_image_zone(self):
        zone = QFrame()
        zone.setMinimumHeight(160)
        zone.setMaximumHeight(220)
        zone.setStyleSheet("""
            QFrame {
                background: #141824;
                border: 2px dashed #2d3555;
                border-radius: 14px;
            }
            QFrame:hover {
                border-color: #6366f1;
            }
        """)
        zone.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QVBoxLayout(zone)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        self.zone_icon = QLabel("🖼️")
        self.zone_icon.setStyleSheet("font-size: 36px;")
        self.zone_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zone_text = QLabel("Click to select image")
        self.zone_text.setStyleSheet("color: #718096; font-size: 14px;")
        self.zone_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zone_sub = QLabel("PNG, JPG, GIF, WebP · Max 10MB")
        self.zone_sub.setStyleSheet("color: #4a5568; font-size: 11px;")
        self.zone_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zone_image_preview = QLabel()
        self.zone_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zone_image_preview.setMaximumHeight(140)
        self.zone_image_preview.setVisible(False)

        self.zone_clear = QPushButton("✕  Remove image")
        self.zone_clear.setVisible(False)
        self.zone_clear.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
                max-width: 140px;
            }
        """)
        self.zone_clear.clicked.connect(self._clear_image)

        layout.addWidget(self.zone_icon)
        layout.addWidget(self.zone_text)
        layout.addWidget(self.zone_sub)
        layout.addWidget(self.zone_image_preview)
        layout.addWidget(self.zone_clear, alignment=Qt.AlignmentFlag.AlignCenter)

        # Click to open
        zone.mousePressEvent = lambda e: self._browse_image()

        return zone

    def _build_preview_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background: #0a0d14; border-left: 1px solid #1e2337;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 28, 28, 28)

        header_row = QHBoxLayout()
        lbl = QLabel("PREVIEW")
        lbl.setStyleSheet("color: #4a5568; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        header_row.addWidget(lbl)
        header_row.addStretch()

        self.preview_platform_combo = QComboBox()
        for k, v in PLATFORMS.items():
            self.preview_platform_combo.addItem(f"{v['icon']} {v['label']}", k)
        self.preview_platform_combo.currentIndexChanged.connect(self._update_preview_platform)
        header_row.addWidget(self.preview_platform_combo)
        layout.addLayout(header_row)

        # Preview card
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self.preview_widget = SocialPostPreview("mastodon")
        scroll.setWidget(self.preview_widget)
        layout.addWidget(scroll)

        return panel

    # ── Accounts Page ─────────────────────────────────────────────────────────

    def _build_accounts_page(self):
        page = QWidget()
        page.setStyleSheet("background: #0f1117;")
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(32, 32, 32, 32)

        header_row = QHBoxLayout()
        title = QLabel("Accounts")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #f8fafc;")
        header_row.addWidget(title)
        header_row.addStretch()

        add_btn = QPushButton("+ Add Account")
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._add_account_dialog)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        subtitle = QLabel("Connect your social media accounts to enable cross-posting.")
        subtitle.setStyleSheet("color: #718096; font-size: 14px;")
        layout.addWidget(subtitle)

        # Platform info
        info_grid = QGridLayout()
        info_grid.setSpacing(12)
        for i, (k, v) in enumerate(PLATFORMS.items()):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: #141824;
                    border: 1px solid #2d3555;
                    border-radius: 12px;
                    padding: 4px;
                }}
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(14, 12, 14, 12)
            icon_lbl = QLabel(v["icon"])
            icon_lbl.setStyleSheet("font-size: 22px;")
            name_lbl = QLabel(v["label"])
            name_lbl.setStyleSheet(f"color: {v['color']}; font-weight: 700; font-size: 14px;")
            limit_lbl = QLabel(f"{v['char_limit']} chars")
            limit_lbl.setStyleSheet("color: #4a5568; font-size: 12px;")
            c_layout.addWidget(icon_lbl)
            c_layout.addWidget(name_lbl)
            c_layout.addStretch()
            c_layout.addWidget(limit_lbl)
            info_grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(info_grid)

        acct_label = QLabel("CONNECTED ACCOUNTS")
        acct_label.setStyleSheet("color: #4a5568; font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-top: 8px;")
        layout.addWidget(acct_label)

        # Accounts list
        self.accounts_scroll_main = QScrollArea()
        self.accounts_scroll_main.setWidgetResizable(True)
        self.accounts_scroll_main.setStyleSheet("border: 1px solid #2d3555; border-radius: 12px; background: #141824;")
        self.accounts_container = QWidget()
        self.accounts_container.setStyleSheet("background: transparent;")
        self.accounts_container_layout = QVBoxLayout(self.accounts_container)
        self.accounts_container_layout.setSpacing(8)
        self.accounts_container_layout.setContentsMargins(12, 12, 12, 12)
        self.accounts_scroll_main.setWidget(self.accounts_container)
        layout.addWidget(self.accounts_scroll_main)

        return page

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp)"
        )
        if path:
            self._set_image(path)

    def _set_image(self, path):
        self.image_path = path
        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", "Could not load image.")
            return

        self.image_pixmap = pixmap

        # Update zone
        scaled = pixmap.scaled(400, 140, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.zone_image_preview.setPixmap(scaled)
        self.zone_image_preview.setVisible(True)
        self.zone_icon.setVisible(False)
        self.zone_text.setText(os.path.basename(path))
        self.zone_sub.setVisible(False)
        self.zone_clear.setVisible(True)

        # Update preview
        self.preview_widget.set_image(pixmap)

    def _clear_image(self):
        self.image_path = None
        self.image_pixmap = None
        self.zone_image_preview.setPixmap(QPixmap())
        self.zone_image_preview.setVisible(False)
        self.zone_icon.setVisible(True)
        self.zone_text.setText("Click to select image")
        self.zone_sub.setVisible(True)
        self.zone_clear.setVisible(False)
        self.preview_widget.set_image(None)

    def _on_text_changed(self):
        text = self.caption_edit.toPlainText()
        self.char_counter.setText(f"{len(text)} / 500")
        self.preview_widget.set_text(text)
        # Update all compose checkboxes text
        for cb in self._get_selected_checkboxes(all_of_them=True):
            pass  # handled by preview

    def _update_preview_platform(self):
        key = self.preview_platform_combo.currentData()
        self.preview_widget.set_platform(key)
        self.preview_widget.set_text(self.caption_edit.toPlainText())
        if self.image_pixmap:
            self.preview_widget.set_image(self.image_pixmap)

        # Set username from matching account
        for account in self.config.get_accounts():
            if account["platform"] == key:
                self.preview_widget.set_username(account.get("username", "@you"))
                break

    def _get_selected_checkboxes(self, all_of_them=False):
        result = []
        for i in range(self.accounts_list_layout.count()):
            item = self.accounts_list_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                cb = w.findChild(QCheckBox)
                if cb and (all_of_them or cb.isChecked()):
                    result.append(cb)
        return result

    def _refresh_accounts(self):
        # Clear compose list
        while self.accounts_list_layout.count():
            item = self.accounts_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear accounts page list
        while self.accounts_container_layout.count():
            item = self.accounts_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        accounts = self.config.get_accounts()

        if not accounts:
            empty = QLabel("No accounts yet. Add one in the Accounts tab.")
            empty.setStyleSheet("color: #4a5568; padding: 20px; font-size: 13px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.accounts_list_layout.addWidget(empty)

            empty2 = QLabel("Click '+ Add Account' to get started.")
            empty2.setStyleSheet("color: #4a5568; padding: 30px; font-size: 14px;")
            empty2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.accounts_container_layout.addWidget(empty2)
        else:
            for i, account in enumerate(accounts):
                # Compose checkbox row
                self._add_compose_account_row(account, i)
                # Accounts page row
                self._add_account_management_row(account, i)

        self.accounts_list_layout.addStretch()
        self.accounts_container_layout.addStretch()

    def _add_compose_account_row(self, account, idx):
        p = PLATFORMS.get(account["platform"], PLATFORMS["mastodon"])
        row = QFrame()
        row.setStyleSheet("""
            QFrame { background: #1a1f2e; border-radius: 10px; }
            QFrame:hover { background: #1e2337; }
        """)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 10, 12, 10)
        rl.setSpacing(10)

        cb = QCheckBox()
        cb.setChecked(True)
        cb.setProperty("account_idx", idx)

        icon = QLabel(p["icon"])
        icon.setStyleSheet("font-size: 16px;")

        name = QLabel(f"{account['username']}")
        name.setStyleSheet("color: #e2e8f0; font-size: 13px; font-weight: 500;")

        badge = QLabel(p["label"])
        badge.setStyleSheet(f"color: {p['color']}; font-size: 11px; font-weight: 600; background: rgba(99,102,241,0.1); padding: 2px 8px; border-radius: 6px;")

        rl.addWidget(cb)
        rl.addWidget(icon)
        rl.addWidget(name)
        rl.addStretch()
        rl.addWidget(badge)
        self.accounts_list_layout.addWidget(row)

    def _add_account_management_row(self, account, idx):
        p = PLATFORMS.get(account["platform"], PLATFORMS["mastodon"])
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background: #1a1f2e;
                border: 1px solid #2d3555;
                border-radius: 12px;
            }
        """)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(16, 14, 16, 14)
        rl.setSpacing(12)

        icon = QLabel(p["icon"])
        icon.setStyleSheet("font-size: 22px;")
        icon.setFixedWidth(30)

        info = QVBoxLayout()
        name_lbl = QLabel(account.get("username", "Unknown"))
        name_lbl.setStyleSheet("color: #f8fafc; font-weight: 600; font-size: 14px;")
        platform_lbl = QLabel(p["label"] + (f"  ·  {account.get('instance','')}" if account.get("instance") else ""))
        platform_lbl.setStyleSheet("color: #718096; font-size: 12px;")
        info.addWidget(name_lbl)
        info.addWidget(platform_lbl)

        del_btn = QPushButton("Remove")
        del_btn.setFixedHeight(34)
        del_btn.setProperty("class", "danger")
        del_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239,68,68,0.15);
                color: #ef4444;
                border: 1px solid rgba(239,68,68,0.3);
                border-radius: 8px;
                padding: 4px 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #ef4444;
                color: white;
            }
        """)
        del_btn.clicked.connect(lambda checked, i=idx: self._remove_account(i))

        rl.addWidget(icon)
        rl.addLayout(info)
        rl.addStretch()
        rl.addWidget(del_btn)

        self.accounts_container_layout.addWidget(row)

    def _add_account_dialog(self):
        dlg = AddAccountDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_account:
            self.config.add_account(dlg.result_account)
            self._refresh_accounts()

    def _remove_account(self, idx):
        reply = QMessageBox.question(self, "Remove Account",
                                     "Are you sure you want to remove this account?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.config.remove_account(idx)
            self._refresh_accounts()

    def _post(self):
        text = self.caption_edit.toPlainText().strip()
        if not text and not self.image_path:
            QMessageBox.warning(self, "Nothing to Post", "Please add a caption or image before posting.")
            return

        # Collect selected accounts
        selected_accounts = []
        accounts = self.config.get_accounts()
        for i in range(self.accounts_list_layout.count()):
            item = self.accounts_list_layout.itemAt(i)
            if item and item.widget():
                cb = item.widget().findChild(QCheckBox)
                if cb and cb.isChecked():
                    account_idx = cb.property("account_idx")
                    if account_idx is not None and account_idx < len(accounts):
                        selected_accounts.append(accounts[account_idx])

        if not selected_accounts:
            QMessageBox.warning(self, "No Accounts Selected", "Please select at least one account to post to.")
            return

        # Clear progress area
        while self.progress_area.layout().count():
            item = self.progress_area.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.progress_labels = {}
        for account in selected_accounts:
            p = PLATFORMS.get(account["platform"], PLATFORMS["mastodon"])
            key = f"{account['platform']}:{account['username']}"

            row = QHBoxLayout()
            icon_lbl = QLabel(p["icon"])
            name_lbl = QLabel(account["username"])
            name_lbl.setStyleSheet("color: #a0aec0; font-size: 12px;")
            status_lbl = QLabel("Waiting…")
            status_lbl.setStyleSheet("color: #4a5568; font-size: 12px;")
            row.addWidget(icon_lbl)
            row.addWidget(name_lbl)
            row.addStretch()
            row.addWidget(status_lbl)

            bar = QProgressBar()
            bar.setRange(0, 0)  # indeterminate
            bar.setFixedHeight(4)

            container = QWidget()
            cl = QVBoxLayout(container)
            cl.setSpacing(4)
            cl.setContentsMargins(0,0,0,0)
            cl.addLayout(row)
            cl.addWidget(bar)

            self.progress_area.layout().addWidget(container)
            self.progress_labels[key] = (status_lbl, bar)

        self.progress_area.setVisible(True)
        self.post_btn.setEnabled(False)
        self.post_btn.setText("Posting…")

        # Start worker
        self.worker = PostWorker(
            selected_accounts,
            text,
            self.image_path,
            self.alt_edit.text().strip()
        )
        self.worker.progress.connect(self._on_post_progress)
        self.worker.done.connect(self._on_post_done)
        self.worker.start()

    def _on_post_progress(self, key, message):
        if key in self.progress_labels:
            lbl, bar = self.progress_labels[key]
            lbl.setText(message)
            if "✓" in message:
                lbl.setStyleSheet("color: #10b981; font-size: 12px;")
                bar.setRange(0, 1)
                bar.setValue(1)
            elif "✗" in message:
                lbl.setStyleSheet("color: #ef4444; font-size: 12px;")
                bar.setRange(0, 1)
                bar.setValue(0)

    def _on_post_done(self, results):
        self.post_btn.setEnabled(True)
        self.post_btn.setText("🚀  Post to Selected Platforms")

        ok_count = sum(1 for r in results.values() if r["ok"])
        fail_count = len(results) - ok_count

        if fail_count == 0:
            QMessageBox.information(self, "Posted!", f"Successfully posted to {ok_count} platform(s)!")
        else:
            msg = f"Posted to {ok_count} platform(s)."
            if fail_count:
                msg += f"\n{fail_count} failed — check progress area for details."
            QMessageBox.warning(self, "Partial Success", msg)


# ─── Entry ────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SocialSync")
    app.setOrganizationName("SocialSync")

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0f1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#1a1f2e"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#141824"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1a1f2e"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1a1f2e"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#f8fafc"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#6366f1"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#6366f1"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
