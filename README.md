# Professional Telethon Session Utility

The Telegram bot provides a menu, help, security guidance, and an owner-only `/telegram` command.

For account safety, OTPs, 2FA passwords, and session strings are **not collected by the bot**.

## Environment variables

- `BOT_TOKEN`
- `API_ID`
- `API_HASH`

## Commands

- `/start`
- `/tele`
- `/telegram` (owner only: Telegram ID `7998217405`)
- `/help`
- `/cancel`

## Local session generation

Run `python local_session.py` on a trusted device. Credentials stay in the local terminal and the resulting session string is printed locally.
