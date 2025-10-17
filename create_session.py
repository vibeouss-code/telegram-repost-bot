from telethon import TelegramClient
import asyncio

# Your credentials
API_ID = 29288825
API_HASH = "aef990ed594ffffae5891bb46d5d24a2"

async def create_session():
    print("Creating Telegram session...")
    client = TelegramClient('bot_session', API_ID, API_HASH)
    
    await client.start()
    
    print("✅ Session created successfully!")
    print("📁 File 'bot_session.session' has been created")
    
    await client.disconnect()

asyncio.run(create_session())