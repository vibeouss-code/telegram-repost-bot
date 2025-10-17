import asyncio
import logging
import os
import sys
from telethon import TelegramClient, events
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramRepostBot:
    def __init__(self):
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.source_channel = os.getenv('SOURCE_CHANNEL', '')
        self.target_channel = os.getenv('TARGET_CHANNEL', '')
        
        if not all([self.api_id, self.api_hash, self.source_channel, self.target_channel]):
            logger.error("❌ Missing environment variables!")
            sys.exit(1)
        
        self.client = TelegramClient('bot_session', self.api_id, self.api_hash)
        self.stats = {'posted': 0, 'failed': 0}
    
    async def start(self):
        try:
            logger.info("🚀 Starting bot...")
            await self.client.start()
            
            self.source = await self.client.get_entity(self.source_channel)
            self.target = await self.client.get_entity(self.target_channel)
            
            logger.info(f"📡 Source: {self.source.title}")
            logger.info(f"🎯 Target: {self.target.title}")
            
            @self.client.on(events.NewMessage(chats=self.source))
            async def repost(event):
                await self.repost_content(event)
            
            logger.info("✅ Bot is active and monitoring!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    async def repost_content(self, event):
        message = event.message
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        try:
            if message.media:
                await self.client.send_file(
                    self.target,
                    message.media,
                    caption=message.text or ""
                )
                logger.info(f"✅ [{timestamp}] Posted media to {self.target.title}")
            elif message.text:
                await self.client.send_message(self.target, message.text)
                logger.info(f"✅ [{timestamp}] Posted text to {self.target.title}")
            
            self.stats['posted'] += 1
            logger.info(f"📊 Total posted: {self.stats['posted']}")
            
        except Exception as e:
            logger.error(f"❌ [{timestamp}] Failed: {e}")
            self.stats['failed'] += 1
    
    async def run_forever(self):
        while True:
            try:
                if await self.start():
                    await self.client.run_until_disconnected()
            except Exception as e:
                logger.error(f"💥 Disconnected: {e}")
                await asyncio.sleep(30)
            
            if self.client.is_connected():
                await self.client.disconnect()
            await asyncio.sleep(10)

async def main():
    print("=" * 60)
    print("🤖 TELEGRAM AUTO-REPOST BOT")
    print("=" * 60)
    print(f"Source: {os.getenv('SOURCE_CHANNEL')}")
    print(f"Target: {os.getenv('TARGET_CHANNEL')}")
    print("=" * 60)
    
    bot = TelegramRepostBot()
    await bot.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
