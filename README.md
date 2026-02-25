# ⬡ SocialSync

> Cross-post photos to Mastodon, Pixelfed, Bluesky, and Threads — all from one beautiful Linux desktop app.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-green?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%2F%20Linux-orange?logo=linux&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## ✨ Features

- 🖼️ **Image upload** — click to select PNG, JPG, GIF, or WebP
- ✍️ **Caption editor** with per-platform character counters
- 👁️ **Live post preview** — see exactly how your post will look on each platform before sending
- ♿ **Alt text** support for screen reader accessibility
- ✅ **Selective posting** — choose which accounts receive each post
- 📊 **Real-time progress** — per-account status bars while posting
- 👤 **Multiple accounts** — add multiple Mastodon/Pixelfed instances
- 🔒 **Local credential storage** — tokens never leave your machine
- 🌙 **Modern dark UI** — built with PyQt6, looks great on GNOME, KDE, and XFCE

---

## 📦 Supported Platforms

| Platform | Auth | Char Limit |
|----------|------|-----------|
| 🐘 Mastodon | Access Token | 500 |
| 📸 Pixelfed | Access Token | 2,200 |
| 🦋 Bluesky | App Password | 300 |
| @ Threads | Graph API Token | 500 |

---

## 🚀 Installation

### Requirements

- Ubuntu 20.04+ (or any Linux with Python 3.8+)
- Python 3.8 or higher
- pip3

### Quick Install

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/socialsync.git
cd socialsync

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Run the app
python3 socialsync.py
```

### One-liner (no clone needed)

```bash
pip3 install PyQt6 requests Pillow --break-system-packages && python3 socialsync.py
```

### Add to App Launcher (optional)

```bash
chmod +x install.sh
./install.sh
```

This creates a `.desktop` entry so SocialSync appears in your GNOME/KDE/XFCE application menu.

---

## 🔧 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `PyQt6` | ≥6.4 | GUI framework |
| `requests` | ≥2.28 | HTTP API calls |
| `Pillow` | ≥9.0 | Image handling |

Install all at once:

```bash
pip3 install -r requirements.txt
```

---

## 🔑 Getting API Credentials

### 🐘 Mastodon

1. Log in to your Mastodon instance
2. Go to **Settings** → **Development** → **New Application**
3. Give it a name (e.g. "SocialSync")
4. Enable scopes: `read`, `write`, `follow`
5. Click **Submit** and copy the **Access Token**

In SocialSync:
- **Username**: `@yourhandle@instance.social`
- **Instance URL**: `https://mastodon.social` (or your instance)
- **Access Token**: paste the token

---

### 📸 Pixelfed

1. Log in to your Pixelfed instance (e.g. pixelfed.social)
2. Go to **Settings** → **Applications** → **New Application**
3. Enable `read` and `write` scopes
4. Copy the **Access Token**

In SocialSync:
- **Username**: `@yourhandle@pixelfed.social`
- **Instance URL**: `https://pixelfed.social`
- **Access Token**: paste the token

---

### 🦋 Bluesky

1. Log in to [bsky.app](https://bsky.app)
2. Go to **Settings** → **Privacy and Security** → **App Passwords**
3. Click **Add App Password**, give it a name
4. Copy the generated password (format: `xxxx-xxxx-xxxx-xxxx`)

> ⚠️ Use the **App Password**, NOT your main account password.

In SocialSync:
- **Username**: `yourhandle.bsky.social`
- **App Password**: paste the app password

---

### @ Threads

Threads requires a Meta Developer account and uses the official Threads API.

1. Go to [developers.facebook.com](https://developers.facebook.com) and create an account
2. Create a new App → Add the **Threads API** product
3. Under Threads API → **Roles** → add yourself as a tester
4. Generate a **Long-lived Access Token** via the Graph API Explorer
5. Find your **Threads User ID** in the API Explorer (`/me?fields=id`)

In SocialSync:
- **Username**: `@yourhandle`
- **Threads User ID**: your numeric user ID
- **Access Token**: your long-lived token
- **Public Image URL** *(optional)*: Threads requires images to be hosted at a public URL — paste the URL here if you want to include images

> 💡 For image hosting, consider [Imgur](https://imgur.com), an S3 bucket, or your own web server.

---

## 🖥️ How to Use

### 1. Add Your Accounts
Click **Accounts** in the sidebar → **+ Add Account** → select your platform and fill in credentials.

### 2. Compose a Post
Click **Compose** in the sidebar:
- Click the image zone to pick a photo
- Write your caption in the text box
- Add alt text for accessibility
- Check/uncheck accounts in the "Post To" section

### 3. Preview
Use the **Preview** panel on the right — switch the dropdown to see how your post looks on each platform with your actual image and caption.

### 4. Post
Click **🚀 Post to Selected Platforms** — watch the progress bars as each account is posted to.

---

## 📁 File Structure

```
socialsync/
├── socialsync.py          # Main application (single file)
├── requirements.txt       # Python dependencies
├── install.sh             # Desktop launcher installer
├── README.md              # This file
├── LICENSE                # MIT License
├── .github/
│   └── workflows/
│       └── lint.yml       # GitHub Actions: lint on push
└── docs/
    └── CREDENTIALS.md     # Detailed credential setup guide
```

---

## 🔒 Privacy & Security

- All credentials are stored **locally** at `~/.config/socialsync/config.json`
- Tokens are stored in plaintext — keep this file private
- No telemetry, no analytics, no external servers
- All API calls go **directly** to each platform's official API

> To revoke access at any time, delete the app's access token from each platform's settings.

---

## 🛠️ Troubleshooting

**`No module named PyQt6`**
```bash
pip3 install PyQt6 --break-system-packages
```

**`No module named pip`**
```bash
sudo apt install python3-pip
```

**App won't start / display error**
```bash
# Make sure you have a display server running (X11 or Wayland)
echo $DISPLAY  # Should show :0 or similar
```

**Bluesky returns 401 Unauthorized**
→ Make sure you're using an App Password, not your login password.

**Mastodon/Pixelfed returns 422**
→ Your token may be missing `write` scope. Create a new application with all required scopes.

**Threads image won't post**
→ Threads requires a publicly accessible image URL. Local file paths don't work with the Threads API.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with [PyQt6](https://pypi.org/project/PyQt6/), using the official APIs of Mastodon, Pixelfed, Bluesky AT Protocol, and Meta Threads API.
