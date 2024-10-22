from flask import Flask, request, jsonify
from telethon import events, Button
from telethon.errors import UserNotParticipantError
import re
import logging
from telegram import Bot  # Import Telegram Bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "7717941076:AAEcwFEbve3HjqSfTJHZLax68JOEceItMQk"

# Channel configurations
SOURCE_CHANNELS = ['@gemz_combo_daily', '@MemefiCode', '@DogMonster']
TARGET_CHANNEL = '@IntroductionofAirdrop'
SPONSOR_CHANNEL = '@IntroductionofAirdrop'

# Initialize Flask and Telegram bot
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

class MessageHandler:
    @staticmethod
    def remove_links(text):
        """Remove URLs from text while preserving other content"""
        if not text:
            return ""
        return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    @staticmethod
    def sanitize_message(text):
        """Sanitize message content"""
        if not text:
            return ""
        text = re.sub(r'<[^>]*>', '', text)  # Remove potential HTML/script injection
        return text.strip()

class UserManager:
    @staticmethod
    async def check_membership(user_id, channel):
        """Check if user is a member of the specified channel"""
        try:
            async with client:
                await client.get_participant(channel, user_id)
            return True
        except UserNotParticipantError:
            return False
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            return False

# Event Handlers
@app.route('/start', methods=['POST'])
def start_handler():
    """Handle /start command"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        welcome_message = f"👋 سلام!\n\nبرای دسترسی به ربات، لطفاً در کانال اسپانسر ما عضو شوید."
        
        bot.send_message(user_id, welcome_message)
        bot.send_message(user_id, "لینک عضویت در کانال اسپانسر: https://t.me/{}".format(SPONSOR_CHANNEL))
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        return jsonify({"error": "متأسفانه خطایی رخ داد. لطفاً بعداً تلاش کنید."}), 500

@app.route('/message', methods=['POST'])
def message_handler():
    """Handle incoming channel messages"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        chat_id = data.get('chat_id')
        message_text = data.get('message')
        
        if not chat_id or not message_text:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Sanitize message
        message_text = MessageHandler.sanitize_message(message_text)
        
        # Send message
        bot.send_message(chat_id=TARGET_CHANNEL, text=message_text)
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"API Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context='adhoc'  # Enable HTTPS
    )
