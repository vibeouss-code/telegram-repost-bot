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
        
        # Support multiple target channels (comma-separated)
        targets = os.getenv('TARGET_CHANNELS', '')
        self.target_channels = [ch.strip() for ch in targets.split(',') if ch.strip()]
        
        if not all([self.api_id, self.api_hash, self.source_channel]):
            logger.error("❌ Missing environment variables!")
            sys.exit(1)
        
        if not self.target_channels:
            logger.error("❌ No target channels specified!")
            sys.exit(1)
        
        self.client = TelegramClient('bot_session', self.api_id, self.api_hash)
        self.source_entity = None
        self.target_entities = []
        self.stats = {'posted': 0, 'failed': 0}
    
    async def start(self):
        try:
            logger.info("🚀 Starting bot...")
            await self.client.start()
            
            # Get source channel
            self.source_entity = await self.client.get_entity(self.source_channel)
            logger.info(f"📡 Source: {self.source_entity.title}")
            
            # Get all target channels
            for i, channel in enumerate(self.target_channels, 1):
                try:
                    entity = await self.client.get_entity(channel)
                    self.target_entities.append(entity)
                    logger.info(f"🎯 Target {i}: {entity.title}")
                except Exception as e:
                    logger.error(f"❌ Cannot connect to '{channel}': {e}")
            
            if not self.target_entities:
                logger.error("❌ No valid target channels!")
                return False
            
            # Register event handler
            @self.client.on(events.NewMessage(chats=self.source_entity))
            async def repost(event):
                await self.repost_to_all(event)
            
            logger.info(f"✅ Bot active! Monitoring {self.source_entity.title}")
            logger.info(f"✅ Will repost to {len(self.target_entities)} channel(s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    async def repost_to_all(self, event):
        """Repost content to all target channels"""
        message = event.message
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        success = 0
        failed = 0
        
        for target in self.target_entities:
            try:
                if message.media:
                    await self.client.send_file(
                        target,
                        message.media,
                        caption=message.text or ""
                    )
                elif message.text:
                    await self.client.send_message(target, message.text)
                
                logger.info(f"✅ [{timestamp}] Posted to {target.title}")
                success += 1
                
                # Delay to avoid rate limits
                await asyncio.sleep(1.5)
                
            except Exception as e:
                logger.error(f"❌ [{timestamp}] Failed to post to {target.title}: {e}")
                failed += 1
        
        self.stats['posted'] += success
        self.stats['failed'] += failed
        
        logger.info(f"📊 [{timestamp}] Result: {success} success, {failed} failed")
        logger.info(f"📈 Total: {self.stats['posted']} posted, {self.stats['failed']} failed")
    
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
    print("🤖 TELEGRAM AUTO-REPOST BOT - MULTI-TARGET")
    print("=" * 60)
    print(f"Source: {os.getenv('SOURCE_CHANNEL')}")
    print(f"Targets: {os.getenv('TARGET_CHANNELS')}")
    print("=" * 60)
    
    bot = TelegramRepostBot()
    await bot.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
