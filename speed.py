from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_OWNER_ID = 5705487207

def start(update, context):
    if update.effective_chat.type == 'private':
        keyboard = [[InlineKeyboardButton("أضفني لمجموعتك", url="https://t.me/speds_bot?startgroup=True")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("مرحبًا! أنا البوت الخاص بردود الفعل التفاعلية. يمكنك استخدام الأمر /set لتعيين رد فعلك المفضل.", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("أضفني لمجموعتك", url="https://t.me/speds_bot?startgroup=True")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("مرحبًا! أنا البوت الخاص بردود الفعل التفاعلية. يمكنك استخدام الأمر /set لتعيين رد فعلك المفضل.", reply_markup=reply_markup)

def add_reaction_to_message(update, context):
    if update.message:
        chat_id = update.effective_chat.id
        message_id = update.message.message_id

        emoji = context.bot_data.get(chat_id, '❤️‍🔥')

        url = f"https://api.telegram.org/bot{context.bot.token}/setMessageReaction"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{
                'type': 'emoji',
                'emoji': emoji
            }]
        }

        try:
            response = requests.post(url, json=data)
            result = response.json()
            if not result['ok']:
                logger.error(f"Failed to add reaction: {result['description']}")
                if result['error_code'] == 429:
                    retry_after = result['parameters']['retry_after']
                    logger.info(f"Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    add_reaction_to_message(update, context)
        except Exception as e:
            logger.error(f"Exception while adding reaction: {e}")

def promote_to_admin(update, context):
    if update.message:
        chat_id = update.effective_chat.id
        user_id = update.message.from_user.id
        try:
            context.bot.promote_chat_member(chat_id, user_id, can_change_info=True, can_delete_messages=True, can_invite_users=True, can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        except Exception as e:
            logger.error(f"Exception while promoting to admin: {e}")

def set_emoji(update, context):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    if user_id != BOT_OWNER_ID:
        chat_admins = context.bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in chat_admins]
        if user_id not in admin_ids:
            update.message.reply_text("هذا الأمر مخصص للمسؤولين فقط.")
            return

    if context.args:
        new_emoji = context.args[0]
        context.bot_data[chat_id] = new_emoji
        update.message.reply_text(f"تم تعيين الإيموجي التفاعلي إلى: {new_emoji} في هذه المجموعة.")
    else:
        update.message.reply_text("يرجى تقديم إيموجي. الاستخدام: /set <emoji>")

def main():
    updater = Updater("7001010995:AAEUGG_LGPTFhO1mPcc9m7fxwZRABKo-8Xg", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('set', set_emoji))  # إضافة هندلر لأمر /set
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, add_reaction_to_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
