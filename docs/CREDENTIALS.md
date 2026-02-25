# 🔑 Credential Setup Guide

Detailed instructions for getting API tokens for each supported platform.

---

## 🐘 Mastodon

Mastodon uses OAuth2. You'll create an "application" on your instance to get a token.

### Steps

1. Log in to your Mastodon instance (e.g. `mastodon.social`, `fosstodon.org`, etc.)
2. Click your profile icon → **Preferences** (or **Settings**)
3. In the left sidebar, click **Development**
4. Click **New application**
5. Fill in:
   - **Application name**: `SocialSync` (or anything you like)
   - **Application website**: leave blank or put your GitHub URL
   - **Redirect URI**: leave as default
   - **Scopes**: check `read`, `write`, `follow`, `push`
6. Click **Submit**
7. Click on your new application to see the tokens
8. Copy the **Your access token** value (the long string at the bottom)

### In SocialSync
- **Username**: `@yourhandle@yourinstance.social`
- **Instance URL**: `https://yourinstance.social`
- **Access Token**: the token you copied

---

## 📸 Pixelfed

Pixelfed uses the same API as Mastodon, so the process is nearly identical.

### Steps

1. Log in to your Pixelfed instance (e.g. `pixelfed.social`)
2. Go to **Settings** → **Applications**
3. Click **Create new token** or **New Application**
4. Fill in the application name
5. Enable scopes: `read`, `write`
6. Save and copy the **Access Token**

### In SocialSync
- **Username**: `@yourhandle@pixelfed.social`
- **Instance URL**: `https://pixelfed.social` (or your instance)
- **Access Token**: the token you copied

---

## 🦋 Bluesky

Bluesky uses App Passwords — a safe way to grant access without sharing your main password.

### Steps

1. Log in to [bsky.app](https://bsky.app)
2. Click your profile → **Settings**
3. Scroll to **Privacy and Security**
4. Click **App Passwords**
5. Click **Add App Password**
6. Give it a descriptive name like `SocialSync`
7. Copy the generated password — it looks like `abcd-efgh-ijkl-mnop`

> ⚠️ This password is shown **once only**. Save it immediately.

### In SocialSync
- **Username**: `yourhandle.bsky.social` (no @ prefix, include the `.bsky.social`)
  - Or your custom domain if you have one: `yourname.com`
- **App Password**: the password you just generated

---

## @ Threads

Threads uses the official Meta Graph API. This is the most involved setup.

### Prerequisites
- A Threads account
- A Meta Developer account (free)

### Steps

#### 1. Create a Meta Developer Account
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **Get Started** and follow the signup flow
3. Verify your account with a phone number if prompted

#### 2. Create an App
1. Go to [My Apps](https://developers.facebook.com/apps)
2. Click **Create App**
3. Select **Other** as the use case → **Next**
4. Select **Business** as the app type → **Next**
5. Give your app a name (e.g. `SocialSync`) → **Create app**

#### 3. Add Threads API
1. In your app dashboard, find **Add products to your app**
2. Find **Threads API** and click **Set up**

#### 4. Add Yourself as a Tester
1. Go to **App Roles** → **Roles**
2. Click **Add People** → **Add Testers**
3. Search for your Threads/Instagram username and add yourself
4. Accept the tester invite on your Threads profile

#### 5. Get Your User ID and Token
1. Go to **Tools** → **Graph API Explorer**
2. In the top-right dropdown, select your app
3. Under **User or Page**, click **Get User Access Token**
4. Select permissions: `threads_basic`, `threads_content_publish`
5. Click **Generate Access Token** and authorize
6. In the query field, type: `me?fields=id,username`
7. Click **Submit** — note your numeric **id**

#### 6. Get a Long-Lived Token
Short-lived tokens expire in 1 hour. Exchange for a long-lived token (60 days):

```bash
curl -X GET "https://graph.threads.net/access_token
  ?grant_type=th_exchange_token
  &client_id=YOUR_APP_ID
  &client_secret=YOUR_APP_SECRET
  &access_token=YOUR_SHORT_LIVED_TOKEN"
```

Replace `YOUR_APP_ID`, `YOUR_APP_SECRET` (from App Settings → Basic), and `YOUR_SHORT_LIVED_TOKEN`.

Copy the `access_token` from the response.

### In SocialSync
- **Username**: `@yourthreadshandle`
- **Threads User ID**: your numeric ID from step 5
- **Access Token**: your long-lived token
- **Public Image URL** *(for images only)*: Threads requires images to be at a public URL.
  Host your image on Imgur, S3, or any public web server and paste the URL here.

> 💡 **Token refresh**: Long-lived tokens last 60 days and can be refreshed before they expire using the `refresh_access_token` endpoint.

---

## 🔒 Security Notes

- Tokens are stored at `~/.config/socialsync/config.json`
- This file is **not** encrypted — protect it like a password
- Never commit this file to git (it's in `.gitignore`)
- To revoke access: delete the token from each platform's settings
- Bluesky App Passwords can be individually revoked in Settings → App Passwords
