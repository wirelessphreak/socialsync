# Contributing to SocialSync

Thanks for your interest in contributing! Here's how to get involved.

## Getting Started

```bash
git clone https://github.com/yourusername/socialsync.git
cd socialsync
pip3 install -r requirements.txt
python3 socialsync.py
```

## How to Contribute

- **Bug reports**: Open an issue with steps to reproduce, your OS, and Python version
- **Feature requests**: Open an issue describing the feature and your use case
- **Pull requests**: Fork → branch → PR against `main`

## Code Style

- Follow PEP 8
- Keep the app as a single file (`socialsync.py`) for easy distribution
- Qt signals/slots for all threading — never block the main thread
- Add a comment block for any new platform's API implementation

## Adding a New Platform

1. Add the platform to the `PLATFORMS` dict at the top of `socialsync.py`
2. Add a `_post_yourplatform()` method to the `PostWorker` class
3. Add credential fields to the `AddAccountDialog._update_fields()` method
4. Update `README.md` and `docs/CREDENTIALS.md` with setup instructions

## Reporting Security Issues

If you find a security vulnerability, please email instead of opening a public issue.
