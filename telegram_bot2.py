from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, filters, MessageHandler as TgMessageHandler
import logging
import re
from typing import List
from dataclasses import dataclass

# تنظیمات لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    """کلاس تنظیمات بات"""
    bot_token: str
    source_channels: List[str]
    target_channel: str
    sponsor_channel: str
    admin_users: List[int]

class MessageProcessor:
    """مدیریت پردازش پیام‌ها"""
    
    @staticmethod
    def sanitize_message(text: str) -> str:
        """تمیزسازی و حذف تگ‌ها"""
        return ' '.join(re.sub(r'<[^>]*>', '', text or '').split()).strip()

    @staticmethod
    def remove_links(text: str) -> str:
        """حذف لینک‌ها"""
        return re.sub(r'http[s]?://\S+', '', text or '')

class TelegramBot:
    def __init__(self, config: BotConfig):
        self.config = config
        self.application = ApplicationBuilder().token(config.bot_token).build()

    def build_keyboard(self):
        """ساخت دکمه‌های کیبورد"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("عضویت در کانال اسپانسر", url=f'https://t.me/{self.config.sponsor_channel.replace("@", "")}')],
            [InlineKeyboardButton("تأیید عضویت", callback_data='verify_membership')]
        ])

    async def start_command(self, update: Update, _):
        """مدیریت دستور /start"""
        try:
            await update.message.reply_text(
                f"👋 سلام {update.effective_user.first_name}!\n\n"
                "برای دسترسی به ربات، لطفاً در کانال اسپانسر ما عضو شوید.",
                reply_markup=self.build_keyboard()
            )
        except Exception as e:
            logger.error(f"خطا در مدیریت start: {e}")
            await update.message.reply_text("خطایی رخ داد. لطفاً بعداً تلاش کنید.")

    async def verify_membership(self, update: Update, _):
        """بررسی عضویت کاربر"""
        try:
            await update.callback_query.answer("عضویت شما با موفقیت تأیید شد!")
        except Exception as e:
            logger.error(f"خطا در تأیید عضویت: {e}")
            await update.callback_query.answer("خطا رخ داد.")

    async def forward_message(self, update: Update, context):
        """ارسال پیام‌های فوروارد شده"""
        try:
            message = update.message
            if not message or message.chat.username not in [ch.replace("@", "") for ch in self.config.source_channels]:
                return
            
            text = MessageProcessor.remove_links(message.text or message.caption)
            text = MessageProcessor.sanitize_message(text)

            kwargs = {"caption": f"{text}\n\nاز: @{message.chat.username}"}

            if message.photo:
                await context.bot.send_photo(self.config.target_channel, photo=message.photo[-1].file_id, **kwargs)
            elif message.video:
                await context.bot.send_video(self.config.target_channel, video=message.video.file_id, **kwargs)
            else:
                await context.bot.send_message(self.config.target_channel, f"{text}\n\nاز: @{message.chat.username}")
        except Exception as e:
            logger.error(f"خطا در ارسال پیام: {e}")

    def run(self):
        """راه‌اندازی بات"""
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CallbackQueryHandler(self.verify_membership, pattern='^verify_membership$'))
        self.application.add_handler(TgMessageHandler(filters.ALL, self.forward_message))

        logger.info("بات در حال اجرا است...")
        self.application.run_polling()

def main():
    config = BotConfig(
        bot_token="7717941076:AAEcwFEbve3HjqSfTJHZLax68JOEceItMQk",  # توکن جدید شما
        source_channels=['@gemz_combo_daily', '@MemefiCode', '@AirDropTelegramProChat'],
        target_channel='@IntroductionofAirdrop',
        sponsor_channel='@IntroductionofAirdrop',
        admin_users=[7060539098]
    )
    
    bot = TelegramBot(config)
    bot.run()

if __name__ == '__main__':
    main()
