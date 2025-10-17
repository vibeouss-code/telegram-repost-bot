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
```

4. Click **"Commit new file"**

### 3.2 Create `requirements.txt`
1. Click **"Add file"** → **"Create new file"**
2. Name: `requirements.txt`
3. Content:
```
telethon==1.34.0
```
4. Click **"Commit new file"**

### 3.3 Create `Procfile`
1. Click **"Add file"** → **"Create new file"**
2. Name: `Procfile` (exactly like this, no extension)
3. Content:
```
worker: python main.py
```
4. Click **"Commit new file"**

### 3.4 Upload Session File
1. Click **"Add file"** → **"Upload files"**
2. Drag and drop `bot_session.session` from your desktop
3. Click **"Commit changes"**

✅ Your repository now has all 4 files!

---

## Step 4: Deploy to Railway

### 4.1 Go to Railway
- Visit: https://railway.app
- Click **"Start a New Project"**

### 4.2 Connect GitHub
1. Click **"Deploy from GitHub repo"**
2. Click **"Login with GitHub"**
3. Authorize Railway
4. Select your **telegram-repost-bot** repository
5. Click **"Deploy Now"**

### 4.3 Wait for Initial Deploy
- Watch the build logs
- Wait until you see "Deployment failed" or similar (this is normal - we need to add variables first)

---

## Step 5: Set Environment Variables in Railway

### 5.1 Go to Variables Tab
1. In Railway dashboard, find your project
2. Click **"Variables"** tab

### 5.2 Add Variables
Click **"+ New Variable"** for each:

**Variable 1:**
- Name: `API_ID`
- Value: `29288825`

**Variable 2:**
- Name: `API_HASH`
- Value: `aef990ed594ffffae5891bb46d5d24a2`

**Variable 3:**
- Name: `SOURCE_CHANNEL`
- Value: `jemla_clothing` (without @)

**Variable 4:**
- Name: `TARGET_CHANNEL`
- Value: `testy_jemla` (without @)

Click **"Add"** after each variable

---

## Step 6: Make Your Bot Admin in Both Channels

### 6.1 For @jemla_clothing (Source)
1. Open the channel in Telegram
2. Click channel name → **"Administrators"**
3. Click **"Add Administrator"**
4. Search for your bot (search by the username you gave it)
5. Give permission: **"Post Messages"** ✅
6. Click **"Save"**

### 6.2 For @testy_jemla (Target)
1. Open the channel in Telegram
2. Click channel name → **"Administrators"**
3. Click **"Add Administrator"**
4. Search for your bot
5. Give permission: **"Post Messages"** ✅
6. Click **"Save"**

---

## Step 7: Redeploy and Monitor

### 7.1 Trigger Redeploy
1. In Railway, go to **"Deployments"** tab
2. Click **"Redeploy"** button

### 7.2 Watch Logs
1. Click on the latest deployment
2. Watch **"Deploy Logs"**

### 7.3 Look for Success Messages
You should see:
```
🚀 Starting bot...
📡 Source: [Your Source Channel Name]
🎯 Target: [Your Target Channel Name]
✅ Bot is active and monitoring!
