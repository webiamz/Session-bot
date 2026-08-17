import os
import asyncio
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from http.server import BaseHTTPRequestHandler, HTTPServer

API_ID = int(os.environ.get("API_ID", 6))
API_HASH = os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# 🔥 REPLIT/RENDER KEEP-ALIVE JUGAAD 🔥
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Session Generator & Spy Bot is Alive 24/7!")
        
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

@bot.on(events.NewMessage)
async def handle_message(event):
    chat_id = event.chat_id
    text = event.text.strip()
    
    # 🔥 NAYA SPY COMMAND (PRIVATE GROUPS SUPPORTED) 🔥
    if text.startswith("/spy"):
        try:
            parts = text.split("|")
            if len(parts) != 2:
                await event.reply("❌ **Galat Format!** Aise bhejo:\n`/spy SESSION_STRING | -1001234567890`")
                return
            
            cmd_part = parts[0].replace("/spy", "").strip()
            group_raw = parts[1].strip()

            if not cmd_part or not group_raw:
                await event.reply("❌ Session String ya Group ID missing hai!")
                return

            # 🔥 PRIVATE GROUP ID FIX 🔥
            target_group = group_raw
            if group_raw.startswith("-100") or group_raw.replace("-","").isdigit():
                try:
                    target_group = int(group_raw)
                except ValueError:
                    pass

            msg = await event.reply(f"🔍 **Spy Mode Active!**\nConnecting to target...")

            spy_client = TelegramClient(
                StringSession(cmd_part), 
                API_ID, 
                API_HASH,
                device_model="iPhone 15 Pro Max",
                system_version="iOS 17.5",
                app_version="10.14.1"
            )
            await spy_client.connect()
            
            if not await spy_client.is_user_authorized():
                await msg.edit("❌ **Session Invalid hai!** Naya session banao.")
                return
            
            await msg.edit(f"✅ Login Success! Bhej raha hu `/extols` in Private Group...")
            await spy_client.send_message(target_group, "/extols")
            
            await msg.edit("⏳ `/extols` bhej diya! Zoro ke reply ka 5 second wait kar raha hu...")
            await asyncio.sleep(5)

            messages = await spy_client.get_messages(target_group, limit=3)
            reply_text = "📥 **Aakhiri 3 Messages Group Se:**\n━━━━━━━━━━━━━━━━━━━━\n"
            
            for m in messages:
                sender = await m.get_sender()
                name = getattr(sender, 'first_name', 'Unknown') if sender else 'Unknown'
                msg_text = m.text or "[No Text / Media]"
                reply_text += f"👤 **{name}**:\n`{msg_text}`\n\n"

            reply_text += "━━━━━━━━━━━━━━━━━━━━\n🏁 **Spy Test Complete!**"
            await event.reply(reply_text)
            await spy_client.disconnect()
            
        except Exception as e:
            await event.reply(f"❌ **Error:** {e}\n*(Agar entity error aaye toh check karo account us group me add hai ya nahi)*")
        return

    # --- NORMAl SESSION GENERATOR LOGIC ---
    if text == "/start":
        await event.reply(
            "🔥 **SlotOps Session & Spy Bot** 🔥\n\n"
            "👉 Naya Session Banane ke liye:\nApna Number bhejo (e.g., `+919876543210`)\n\n"
            "👉 Session Test Karne ke liye:\n`/spy NAYA_SESSION_STRING | -1001234567890`"
        )
        sessions[chat_id] = {"step": "phone"}
        return

    if chat_id not in sessions: return
    state = sessions[chat_id]
    
    if state["step"] == "phone":
        phone = text
        await event.reply("⏳ OTP request bhej raha hu, wait karo...")
        client = TelegramClient(StringSession(), API_ID, API_HASH, device_model="iPhone 15 Pro Max", system_version="iOS 17.5", app_version="10.14.1")
        await client.connect()
        try:
            send_code = await client.send_code_request(phone)
            state["client"] = client
            state["phone"] = phone
            state["phone_code_hash"] = send_code.phone_code_hash
            state["step"] = "otp"
            await event.reply("✅ **OTP Telegram par bhej diya gaya hai!**\n⚠️ OTP ko space ke sath bhejo (e.g., `1 2 3 4 5 6`).")
        except Exception as e:
            await event.reply(f"❌ Error: {e}")
            del sessions[chat_id]
            
    elif state["step"] == "otp":
        otp = text.replace(" ", "")
        client = state["client"]
        try:
            await client.sign_in(state["phone"], otp, phone_code_hash=state["phone_code_hash"])
            session_string = client.session.save()
            await event.reply(f"🎉 **Success! Naya Session:**\n\n`{session_string}`")
            await client.disconnect()
            del sessions[chat_id]
        except SessionPasswordNeededError:
            state["step"] = "password"
            await event.reply("🔒 **Two-Step Verification (2FA)** on hai! Apna password bhejo:")
        except Exception as e:
            await event.reply(f"❌ Error: {e}")
            await client.disconnect()
            del sessions[chat_id]
            
    elif state["step"] == "password":
        password = text
        client = state["client"]
        try:
            await client.sign_in(password=password)
            session_string = client.session.save()
            await event.reply(f"🎉 **Success! Naya Session:**\n\n`{session_string}`")
            await client.disconnect()
            del sessions[chat_id]
        except Exception as e:
            await event.reply(f"❌ Password Error: {e}")
            await client.disconnect()
            del sessions[chat_id]

# 🚀 STARTING SERVICES
print("⚙️ Keep-Alive server start ho raha hai...")
t = threading.Thread(target=run_keep_alive, daemon=True)
t.start()

print("🤖 Session & Spy Bot is LIVE!")
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot.start(bot_token=BOT_TOKEN)
bot.run_until_disconnected()
