from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sessions import StringSession
import asyncio
import logging
import os

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Configuration
class BotConfig:
    # Session string (pre-generated)
    SESSION = "1ApWapzMBu4s3KKd_2JSJ_5wKFWqGHkq2RG7_YWl54RWNv3H9k5PRuTavvvHZHqQYc7FYHBRypE8o7GiR6OzgSnG5Wx5zQOUqGVtoZC7ZQKGAXb5_DHSBDnYQYEJ8PdQLcNfr2l7BwO9vrcOLrmWKLkiEE_-6LVlBiHOIEyoBltQeJDbGkV7vFN6oVPhYPxVnGS7bIt_lAGM3zqqWSgm8RbZ3UlVH5JSB6UicRqTfLgxeJfN9o8jRBF28nz5X3PL_OB3c7pv-U30n-0NI6DnC2LfHJDhbQ0Xf9Dbo5ZpLyGQ6S7FSFvBSSTBYpjP94lhh9S0ZQcOmxFH3CqqSQXvx2YfQ0mHtbAM="
    
    # Telegram API credentials
    API_ID = 27744450
    API_HASH = "0f1f7f4014ebf82ccd3de56db56d96bc"
    BOT_TOKEN = "7717941076:AAEcwFEbve3HjqSfTJHZLax68JOEceItMQk"
    
    # Channel and admin configurations
    CHANNELS = {
        'source': ['@gemz_combo_daily', '@MemefiCode', '@DogMonster'],
        'target': '@IntroductionofAirdrop',
        'required': ['@IntroductionofAirdrop']
    }
    
    ADMIN_IDS = [6505786158]  # Admin user IDs
    
    # Button configurations
    BUTTONS = {
        'start': [
            [Button.url('کانال اصلی', 'https://t.me/IntroductionofAirdrop')],
            [Button.inline('تایید عضویت ✅', 'verify')]
        ],
        'verified': [
            [Button.inline('دسترسی به ربات 🤖', 'menu')]
        ]
    }
    
    # Message templates
    MESSAGES = {
        'welcome': """
👋 سلام به ربات خوش آمدید!

برای استفاده از ربات مراحل زیر را انجام دهید:
1. عضو کانال شوید
2. روی دکمه تایید عضویت کلیک کنید
3. از امکانات ربات استفاده کنید
        """,
        'verified': "✅ عضویت شما تایید شد! اکنون می‌توانید از ربات استفاده کنید.",
        'not_verified': "❌ لطفا ابتدا در کانال‌های ما عضو شوید."
    }

class TelegramBot:
    def __init__(self):
        self.config = BotConfig
        self.client = TelegramClient(
            StringSession(self.config.SESSION),
            self.config.API_ID,
            self.config.API_HASH
        )
    
    async def start(self):
        """Start the bot"""
        await self.client.start(bot_token=self.config.BOT_TOKEN)
        
        # Register handlers
        self.register_handlers()
        
        # Run the bot
        await self.client.run_until_disconnected()
    
    def register_handlers(self):
        """Register message and callback handlers"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await event.respond(
                self.config.MESSAGES['welcome'],
                buttons=self.config.BUTTONS['start']
            )
        
        @self.client.on(events.CallbackQuery(pattern='verify'))
        async def verify_handler(event):
            user_id = event.sender_id
            
            # Check channel memberships
            try:
                for channel in self.config.CHANNELS['required']:
                    participant = await self.client.get_participant(channel, user_id)
                    if not participant:
                        await event.answer(self.config.MESSAGES['not_verified'])
                        return
                
                # If verified, show success message
                await event.edit(
                    self.config.MESSAGES['verified'],
                    buttons=self.config.BUTTONS['verified']
                )
                
            except Exception as e:
                logger.error(f"Verification error: {e}")
                await event.answer("خطا در بررسی عضویت. لطفا دوباره تلاش کنید.")
        
        @self.client.on(events.NewMessage(chats=self.config.CHANNELS['source']))
        async def forward_handler(event):
            try:
                # Forward message to target channel
                await self.client.forward_messages(
                    self.config.CHANNELS['target'],
                    event.message
                )
            except Exception as e:
                logger.error(f"Forward error: {e}")

        @self.client.on(events.CallbackQuery(pattern='menu'))
        async def menu_handler(event):
            channel_link = f"https://t.me/{self.config.CHANNELS['target'][1:]}"
            await event.edit(
                "🤖 به منوی ربات خوش آمدید!\n\n"
                "از این پس پیام‌های کانال‌های منبع به صورت خودکار در کانال مقصد ارسال خواهند شد.",
                buttons=[[Button.url('کانال مقصد', channel_link)]]
            )

def main():
    """Main function to run the bot"""
    try:
        bot = TelegramBot()
        asyncio.run(bot.start())
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == '__main__':
    main()