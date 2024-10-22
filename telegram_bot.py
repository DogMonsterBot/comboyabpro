from flask import Flask, request, jsonify
from telethon import TelegramClient, events, Button
import re

# اطلاعات API تلگرام شما
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
bot_token = '7717941076:AAEcwFEbve3HjqSfTJHZLax68JOEceItMQk'

# لیست کانال‌های مبدا
source_channels = ['@gemz_combo_daily', '@MemefiCode', '@DogMonster']

# کانال مقصد
target_channel_username = '@IntroductionofAirdrop'
# نام کانال اسپانسر
sponsor_channel = '@IntroductionofAirdrop'  # کانال اسپانسر

# اتصال به تلگرام
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# ایجاد Flask app
app = Flask(__name__)

# تابع برای حذف لینک‌ها از متن
def remove_links(text):
    return re.sub(r'http\S+', '', text)

# خوش‌آمدگویی کاربر
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user = await event.get_user()
    welcome_message = f"👋 خوش آمدید، {user.first_name}!\n\nبرای دسترسی به ربات، لطفاً در کانال اسپانسر ما عضو شوید."
    
    # قفل با دکمه شیشه‌ای
    await event.respond(welcome_message, buttons=[
        [Button.url('وارد کانال اسپانسر شوید', f'https://t.me/{sponsor_channel}')],
        [Button.inline('دسترسی به ربات', 'access_bot')]
    ])

# بررسی عضویت کاربر
@client.on(events.CallbackQuery(data='access_bot'))
async def check_membership(event):
    user_id = event.sender_id
    try:
        member = await client.get_participant(sponsor_channel, user_id)
        
        if member:
            # دسترسی به گزینه‌ها پس از تایید عضویت
            access_message = "✅ شما به ربات دسترسی دارید! گزینه‌های زیر را انتخاب کنید:"
            await event.edit(access_message, buttons=[
                [Button.inline('خرید اشتراک', 'buy_subscription')],
                [Button.inline('پرداخت با استار', 'pay_with_stars')],
                [Button.inline('لینک رفرال', 'referral_link')],
                [Button.inline('پشتیبانی', 'support')]
            ])
        else:
            # خطای عدم عضویت در کانال
            await event.edit("❌ شما عضو کانال نشدید. لطفاً ابتدا عضو شوید و دوباره تلاش کنید.")
    except Exception as e:
        await event.edit("❌ خطا در بررسی عضویت. لطفاً دوباره تلاش کنید.")

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

# دکمه خرید اشتراک
@client.on(events.CallbackQuery(data='buy_subscription'))
async def buy_subscription(event):
    await event.answer("🛒 لطفاً پرداخت با ارز TONCOIN را انجام دهید.")

# دکمه پرداخت با استار
@client.on(events.CallbackQuery(data='pay_with_stars'))
async def pay_with_stars(event):
    await event.answer("✨ لطفاً استارزهای خود را به @A19_8_1994 ارسال کنید.")

# دکمه لینک رفرال
@client.on(events.CallbackQuery(data='referral_link'))
async def referral_link(event):
    user_id = event.sender_id
    referral_link = f"https://t.me/your_bot?start={user_id}"
    await event.answer(f"🔗 لینک رفرال شما: {referral_link}")

# دکمه پشتیبانی
@client.on(events.CallbackQuery(data='support'))
async def support(event):
    await event.answer("📩 برای پشتیبانی به @A19_8_1994 مراجعه کنید.")

# ایجاد یک endpoint برای API
@app.route('/api/message', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    message = data.get('message')

    if not chat_id or not message:
        return jsonify({'error': 'چت ID و پیام ضروری هستند.'}), 400

    # ارسال پیام به کاربر
    client.loop.run_until_complete(client.send_message(chat_id, message))
    return jsonify({'success': 'پیام با موفقیت ارسال شد.'}), 200

# اجرای ربات
if __name__ == '__main__':
    client.start()
    app.run(host='0.0.0.0', port=5000)  # API را روی پورت 5000 اجرا کنید
