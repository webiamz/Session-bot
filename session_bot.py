from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import os

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")


# 🔥 REPLIT/RENDER KEEP-ALIVE JUGAAD 🔥
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Session Generator Bot is Alive 24/7! Working smoothly.")
        
    def log_message(self, format, *args):
        pass

def run_keep_alive():
    try:
        server = HTTPServer(('0.0.0.0', 8080), KeepAliveHandler)
        server.serve_forever()
    except Exception:
        pass


bot = TelegramClient("bot_session", API_ID, API_HASH)
sessions = {}

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        "🔥 **SlotOps Private Session Generator** 🔥\n\n"
        "Apna Phone Number bhejo country code ke sath.\n"
        "Example: `+919876543210`"
    )
    sessions[event.chat_id] = {"step": "phone"}

@bot.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.chat_id
    text = event.text.strip()
    
    if text == "/start": return
    if chat_id not in sessions: return
        
    state = sessions[chat_id]
    
    # --- STEP 1: PHONE NUMBER ---
    if state["step"] == "phone":
        phone = text
        await event.reply("⏳ OTP request bhej raha hu, wait karo...")
        
        # iPhone 15 Spoofing In-Built
        client = TelegramClient(
            StringSession(), 
            API_ID, 
            API_HASH,
            device_model="iPhone 15 Pro Max",
            system_version="iOS 17.5",
            app_version="10.14.1"
        )
        await client.connect()
        try:
            send_code = await client.send_code_request(phone)
            state["client"] = client
            state["phone"] = phone
            state["phone_code_hash"] = send_code.phone_code_hash
            state["step"] = "otp"
            await event.reply(
                "✅ **OTP Telegram par bhej diya gaya hai!**\n\n"
                "⚠️ **IMPORTANT:** OTP ko direct mat bhejna, account ban ho sakta hai. Beech mein space daal kar bhejo.\n"
                "Example agar OTP 123456 hai toh bhejo: `1 2 3 4 5 6`"
            )
        except Exception as e:
            await event.reply(f"❌ Error: {e}")
            del sessions[chat_id]
            
    # --- STEP 2: OTP ---
    elif state["step"] == "otp":
        otp = text.replace(" ", "")  # Spaces hata do
        client = state["client"]
        try:
            await client.sign_in(state["phone"], otp, phone_code_hash=state["phone_code_hash"])
            session_string = client.session.save()
            await event.reply(
                f"🎉 **Success! Naya Session Ban Gaya:**\n\n"
                f"`{session_string}`\n\n"
                "*(Security ke liye upar wala OTP message delete kar do)*"
            )
            await client.disconnect()
            del sessions[chat_id]
        except SessionPasswordNeededError:
            state["step"] = "password"
            await event.reply("🔒 **Two-Step Verification (2FA)** on hai! Apna password bhejo:")
        except Exception as e:
            await event.reply(f"❌ Error: {e}")
            await client.disconnect()
            del sessions[chat_id]
            
    # --- STEP 3: 2FA PASSWORD (AGAR HAI TOH) ---
    elif state["step"] == "password":
        password = text
        client = state["client"]
        try:
            await client.sign_in(password=password)
            session_string = client.session.save()
            await event.reply(
                f"🎉 **Success! Naya Session Ban Gaya:**\n\n"
                f"`{session_string}`\n\n"
                "*(Security ke liye upar wala password message delete kar do)*"
            )
            await client.disconnect()
            del sessions[chat_id]
        except Exception as e:
            await event.reply(f"❌ Password Error: {e}")
            await client.disconnect()
            del sessions[chat_id]

# 🚀 STARTING BOTH SERVICES 🚀
print("⚙️ Keep-Alive server start ho raha hai...")
t = threading.Thread(target=run_keep_alive, daemon=True)
t.start()

print("🤖 Session Bot is LIVE! Jao aur Telegram par /start bhejo.")
bot.start(bot_token=BOT_TOKEN)
bot.run_until_disconnected()
