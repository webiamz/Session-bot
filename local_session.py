import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

print("=== Telethon Local Session Generator ===")
api_id = int(input("API ID: ").strip())
api_hash = input("API Hash: ").strip()
phone = input("Phone number (+countrycode...): ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.send_code_request(phone)
    code = input("Telegram OTP: ").strip().replace(" ", "")
    try:
        client.sign_in(phone=phone, code=code)
    except SessionPasswordNeededError:
        password = input("2FA password: ")
        client.sign_in(password=password)

    session = client.session.save()
    print("\nSUCCESS")
    print("Your session string is shown below. Keep it private:\n")
    print(session)
