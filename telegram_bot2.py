from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler as TelegramMessageHandler, filters
import logging
import os
import re
from typing import List
from dataclasses import dataclass

# تنظیمات لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
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

class CustomMessageHandler:
    """مدیریت پردازش و تمیزسازی پیام‌ها"""
    
    @staticmethod
    def sanitize_message(text: str) -> str:
        """تمیزسازی و اعتبارسنجی محتوای پیام"""
        if not text:
            return ""
        text = re.sub(r'<[^>]*>', '', text)
        text = ' '.join(text.split())
        return text.strip()
        
    @staticmethod
    def remove_links(text: str) -> str:
        """حذف URL‌ها با حفظ سایر محتوا"""
        if not text:
            return ""
        return re.sub(r'http[s]?://\S+', '', text)

class TelegramBot:
    def __init__(self, config: BotConfig):
        self.config = config
        self.application = ApplicationBuilder().token(config.bot_token).build()
        
        # دیکشنری برای ذخیره اطلاعات کاربران
        self.user_data = {
            7060539098: {'score': 50, 'invites': 5},  # مثال: شناسه کاربر و اطلاعات مربوطه
            # می‌توانید کاربرهای بیشتری به این دیکشنری اضافه کنید
        }
        
    async def get_user_score(self, user_id: int) -> int:
        """دریافت امتیاز کاربر بر اساس شناسه"""
        return self.user_data.get(user_id, {}).get('score', 0)

    async def get_invites_count(self, user_id: int) -> int:
        """دریافت تعداد دعوت‌شدگان کاربر بر اساس شناسه"""
        return self.user_data.get(user_id, {}).get('invites', 0)

    async def check_score(self, update: Update, context) -> None:
        user_id = update.effective_user.id
        user_score = await self.get_user_score(user_id)  # دریافت امتیاز کاربر
        invites_count = await self.get_invites_count(user_id)  # دریافت تعداد دعوت‌ها

        # ایجاد دکمه‌ها
        keyboard = [
            [InlineKeyboardButton("دریافت لینک ارجاع", callback_data='get_referral_link')],
            [InlineKeyboardButton("تعداد دعوت‌شدگان: " + str(invites_count), callback_data='show_invites')],
            [InlineKeyboardButton("برگشت", callback_data='back')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                text=f"امتیاز شما: {user_score}\n",
                reply_markup=reply_markup
            )
        else:
            await update.callback_query.answer()  # پاسخ به کلیک دکمه
            await update.callback_query.message.reply_text(
                text=f"امتیاز شما: {user_score}\n",
                reply_markup=reply_markup
            )

    async def get_referral_link(self, update: Update, context) -> None:
        user_id = update.effective_user.id
        referral_link = f"https://t.me/your_bot?start={user_id}"  # لینک ارجاع کاربر
        await update.callback_query.answer()  # پاسخ به کلیک دکمه
        await update.callback_query.message.reply_text(
            text=f"لینک ارجاع شما: {referral_link}\nبه هر کاربر که با این لینک عضو شود، 10 امتیاز دریافت می‌کنید."
        )

    async def start_command(self, update: Update, context):
        """مدیریت دستور /start"""
        try:
            keyboard = [
                [InlineKeyboardButton("عضویت در کانال اسپانسر", 
                                    url=f'https://t.me/{self.config.sponsor_channel.replace("@", "")}')],
                [InlineKeyboardButton("تأیید عضویت", callback_data='verify_membership')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"👋 سلام {update.effective_user.first_name}!\n\n"
                "برای دسترسی به ربات، لطفاً در کانال اسپانسر ما عضو شوید.",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطا در مدیریت start: {e}")
            await update.message.reply_text("متأسفانه خطایی رخ داد. لطفاً بعداً تلاش کنید.")

    async def verify_membership(self, update: Update, context):
        """بررسی عضویت کاربر"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            
            # بررسی اینکه کاربر به کانال عضو شده است
            try:
                member = await context.bot.get_chat_member(chat_id=self.config.sponsor_channel, user_id=user_id)
                if member.status in ['member', 'administrator', 'creator']:
                    # ایجاد دکمه‌ها برای تعامل
                    keyboard = self.create_new_keyboard(user_id)

                    # حذف پیام قبلی
                    await query.message.delete()

                    # ارسال پیام جدید با دکمه‌ها
                    await query.message.reply_text(
                        text="🎉 از شما بابت عضویت متشکرم! حالا می‌توانید دکمه را فشار دهید یا رتبه‌بندی خود را بررسی کنید.",
                        reply_markup=keyboard
                    )
                else:
                    # ایجاد دکمه‌های عضویت
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[ 
                        [InlineKeyboardButton(text='عضویت در کانال', url='https://t.me/IntroductionofAirdrop')],
                        [InlineKeyboardButton(text='بررسی عضویت', callback_data='check_subscription')]
                    ])
                    await query.answer(text="خوش آمدید! لطفاً به کانال بپیوندید و سپس عضویت خود را بررسی کنید.", reply_markup=keyboard)
            except Exception as e:
                logger.error(f"خطا در تأیید عضویت: {e}")
                await query.answer("امکان تأیید عضویت وجود ندارد. لطفاً مطمئن شوید که ربات ادمین کانال است و دوباره تلاش کنید.")
        
        except Exception as e:
            logger.error(f"خطا در تأیید عضویت: {e}")
            await query.answer("خطایی رخ داد. لطفاً دوباره تلاش کنید.")

    async def forward_message(self, update: Update, context):
        """مدیریت ارسال مجدد پیام‌ها"""
        try:
            message = update.message
            if not message:
                logger.warning("پیام وجود ندارد در forward_message")
                return

            # بررسی اینکه پیام از کانال‌های منبع است
            if str(message.chat.username) not in [channel.replace("@", "") for channel in self.config.source_channels]:
                logger.warning(f"پیام از کانال غیرمجاز: {message.chat.username}")
                return

            text = CustomMessageHandler.remove_links(message.text or message.caption or "")
            text = CustomMessageHandler.sanitize_message(text)

            # ارسال به کانال مقصد
            if message.photo:
                await context.bot.send_photo(
                    self.config.target_channel,
                    photo=message.photo[-1].file_id,
                    caption=f"{text}\n\nاز: @{message.chat.username}"
                )
            elif message.video:
                await context.bot.send_video(
                    self.config.target_channel,
                    video=message.video.file_id,
                    caption=f"{text}\n\nاز: @{message.chat.username}"
                )
            else:
                await context.bot.send_message(
                    self.config.target_channel,
                    f"{text}\n\nاز: @{message.chat.username}"
                )
                
            logger.info(f"پیام از {message.chat.username} به {self.config.target_channel} ارسال شد.")
            
        except Exception as e:
            logger.error(f"خطا در ارسال پیام: {e}")

    def create_new_keyboard(self, user_id):
        """ایجاد دکمه‌های جدید"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='بررسی امتیاز من', callback_data=f'check_rating_{user_id}')],
            [InlineKeyboardButton(text='درباره ربات', callback_data='about_bot')],
            [InlineKeyboardButton(text='برگشت', callback_data='back')]
        ])

    async def about_bot(self, update: Update, context):
        """مدیریت دکمه درباره ربات"""
        about_text = (
            "🤖 درباره ربات:\n"
            "این ربات به شما کمک می‌کند تا به راحتی از امتیازها و لینک‌های ارجاع خود باخبر شوید.\n"
            "شما می‌توانید:\n"
            "- کامبو های روزانه به صورت خودکار دریافت  خواهد شد\n"
            "- لینک ارجاع دریافت کنید و دوستان خود را دعوت کنید\n"
            "- از طریق عضویت در کانال اسپانسر، امتیاز بیشتری کسب کنید.\n"
            "\n"
            "برای اطلاعات بیشتر می‌توانید باارسال پیام به ای دی @A19_8_1994 ما تماس بگیرید."
        )
        
        await update.callback_query.answer()  # پاسخ به کلیک دکمه
        
        # حذف پیام قبلی
        await update.callback_query.message.delete()

        await update.callback_query.message.reply_text(about_text)

    async def handle_back(self, update: Update, context):
        """مدیریت دکمه برگشت"""
        await update.callback_query.answer()
        keyboard = self.create_new_keyboard(update.callback_query.from_user.id)

        # حذف پیام قبلی
        await update.callback_query.message.delete()

        await update.callback_query.message.reply_text(
            text="لطفاً گزینه مورد نظر را انتخاب کنید:",
            reply_markup=keyboard
        )

    def run(self):
        """اجرای ربات"""
        try:
            # ثبت دستورات
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CallbackQueryHandler(self.verify_membership, pattern='verify_membership'))
            self.application.add_handler(CallbackQueryHandler(self.check_score, pattern='check_rating_'))
            self.application.add_handler(CallbackQueryHandler(self.get_referral_link, pattern='get_referral_link'))
            self.application.add_handler(CallbackQueryHandler(self.about_bot, pattern='about_bot'))
            self.application.add_handler(CallbackQueryHandler(self.handle_back, pattern='back'))
            self.application.add_handler(CallbackQueryHandler(self.forward_message, filters.TEXT & ~filters.COMMAND))
            self.application.add_handler(TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, self.forward_message))

            logger.info("ربات در حال اجراست...")
            self.application.run_polling()
        except Exception as e:
            logger.error(f"خطا در راه‌اندازی ربات: {e}")

if __name__ == "__main__":
    config = BotConfig(
        bot_token="7717941076:AAEcwFEbve3HjqSfTJHZLax68JOEceItMQk",
        source_channels=['@gemz_combo_daily', '@MemefiCode', '@AirDropTelegramProChat'],
        target_channel='@IntroductionofAirdrop',
        sponsor_channel='@IntroductionofAirdrop',
        admin_users=[7060539098]
    )
    
    bot = TelegramBot(config)
    bot.run()
