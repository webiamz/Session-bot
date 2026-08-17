import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import TelegramClient, events, Button

API_ID = int(os.environ.get("API_ID", "6"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = 7998217405

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")
if not API_HASH:
    raise RuntimeError("API_HASH is missing")

class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Session Bot is online")

    def log_message(self, *_):
        pass

def run_keep_alive():
    try:
        HTTPServer(("0.0.0.0", 8080), KeepAliveHandler).serve_forever()
    except Exception:
        pass

bot = TelegramClient("bot_session", API_ID, API_HASH)

HELP_TEXT = (
    "🧭 **Command Center**\n\n"
    "**/start** — Main menu\n"
    "**/tele** — Session generator guide\n"
    "**/telegram** — Owner-only generator guide\n"
    "**/help** — Commands & security\n"
    "**/cancel** — Cancel current operation\n\n"
    "🔐 OTP, 2FA passwords and session strings are never collected by this bot.\n"
    "For account safety, session generation is performed locally on your own device."
)

START_TEXT = (
    "✨ **Session Utility Bot**\n\n"
    "A clean Telethon utility for creating sessions locally and safely.\n\n"
    "Choose an option below 👇"
)

async def send_menu(event):
    await event.respond(
        START_TEXT,
        buttons=[
            [Button.inline("🔐 Session Guide", b"session"), Button.inline("📖 Help", b"help")],
            [Button.inline("🛡️ Security", b"security")],
        ],
    )

@bot.on(events.NewMessage(pattern=r"^/start$"))
async def start(event):
    await send_menu(event)

@bot.on(events.NewMessage(pattern=r"^/help$"))
async def help_cmd(event):
    await event.respond(HELP_TEXT)

@bot.on(events.NewMessage(pattern=r"^/cancel$"))
async def cancel_cmd(event):
    await event.respond("✅ No interactive credential-collection flow is running.")

@bot.on(events.NewMessage(pattern=r"^/tele$"))
async def tele_cmd(event):
    await event.respond(
        "🔐 **/tele — Session Generator**\n\n"
        "This bot does not ask you to send your Telegram OTP, 2FA password, or session string.\n\n"
        "Run the included `local_session.py` on your own PC/phone environment, enter your credentials there, and keep the generated session locally.\n\n"
        "⚠️ Never paste a session string into a public/group chat."
    )

@bot.on(events.NewMessage(pattern=r"^/telegram$"))
async def telegram_cmd(event):
    if event.sender_id != OWNER_ID:
        await event.respond("⛔ **Access denied.** This command is owner-only.")
        return
    await event.respond(
        "👑 **Owner Session Utility**\n\n"
        "Owner ID verified.\n\n"
        "For security, the bot still will not receive your OTP/2FA/session.\n"
        "Use `local_session.py` locally to create the Telethon session."
    )

@bot.on(events.CallbackQuery)
async def callbacks(event):
    data = event.data.decode()
    if data == "session":
        await event.edit(
            "🔐 **Safe Session Flow**\n\n"
            "1. Download/run `local_session.py`.\n"
            "2. Enter API ID + API Hash locally.\n"
            "3. Enter your phone number locally.\n"
            "4. Enter the Telegram OTP locally.\n"
            "5. If enabled, enter 2FA locally.\n"
            "6. The session string is printed locally only.\n\n"
            "🚫 Do not send any of these credentials to this bot."
        )
    elif data == "help":
        await event.edit(HELP_TEXT)
    elif data == "security":
        await event.edit(
            "🛡️ **Security Rules**\n\n"
            "• Never share OTPs.\n"
            "• Never share your 2FA password.\n"
            "• Treat a Telethon session string like a password.\n"
            "• Keep session files private.\n"
            "• Do not use sessions belonging to other people."
        )
    await event.answer()

print("⚙️ Keep-alive server starting...")
threading.Thread(target=run_keep_alive, daemon=True).start()
print("🤖 Session Utility Bot is LIVE!")
bot.start(bot_token=BOT_TOKEN)
bot.run_until_disconnected()
