from telethon import TelegramClient, events
import re

# اطلاعات API تلگرام شما
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
bot_token = '8026191420:AAGkIwuskDtU_opshjhY5DRMRP72Gzg5ojU'

# لیست کانال‌های مبدا
source_channels = ['@gemz_combo_daily', '@MemefiCode', '@DogMonster']

# کانال مقصد
target_channel_username = '@IntroductionofAirdrop'

# اتصال به تلگرام
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# تابع برای حذف لینک‌ها از متن
def remove_links(text):
    return re.sub(r'http\S+', '', text)

# فیلتر برای شناسایی پست‌ها با هشتگ یا لینک از کانال‌های مبدا
@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    message = event.message

    # حذف لینک‌ها از متن
    text = remove_links(message.message)

    # اضافه کردن ID کانال مقصد به متن
    text += f'\n\nارسال شده به: {target_channel_username}'

    # حذف دکمه‌های شیشه‌ای (در صورت وجود)
    if message.buttons:
        message.buttons = None

    # اگر پیام شامل تصویر باشد
    if message.photo:
        await client.send_file(target_channel_username, message.photo, caption=text)
    else:
        await client.send_message(target_channel_username, text)

# اجرای ربات
client.run_until_disconnected()
