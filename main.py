from telebot import TeleBot, types
import pandas as pd
import time
import random
import string
from datetime import datetime
import os

# Define states for the conversation
ASK_NAME, ASK_CONTACT, REDIRECT_VIDEO, SEND_MESSAGE, SET_VIDEO_LINK, ADMIN_PANEL, SEND_BROADCAST, USER_PANEL, SET_REFERRAL_DISCOUNT, CONFIRM_BROADCAST = range(10)

bot = TeleBot("7732224979:AAHotEmAr8WAN00gvqfDpBpusydVBpV7USc")
user_states = {}
video_link = None  # Global variable to store the video link
all_chat_ids = set()  # Set to store all chat IDs
referral_discounts = {}  # Global variable to store referral discounts

# Define admin user IDs
admin_ids = [796307932]  # Replace with actual admin user IDs

# Referral data structure
referral_data = {}

def generate_referral_link(user_id):
    return f"https://t.me/Rustamxon_endokrinbot?start={user_id}"

def is_admin(user_id):
    return user_id in admin_ids

def save_data_to_excel():
    data = []
    for user_id, info in user_states.items():
        data.append({
            'Name': info.get('name', ''),
            'Contact': info.get('contact', ''),
            'Timestamp': info.get('timestamp', '')
        })
    df = pd.DataFrame(data)
    
    # Check if the file exists
    if os.path.exists('user_data.xlsx'):
        existing_df = pd.read_excel('user_data.xlsx')
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_excel('user_data.xlsx', index=False)

def start(message):
    all_chat_ids.add(message.chat.id)  # Add chat ID to the set
    if not is_admin(message.from_user.id):
        if 'name' not in user_states.get(message.chat.id, {}):
            bot.send_message(message.chat.id, "Iltimos, ismingiz va familiyangizni kiriting: ✍️")
            user_states[message.chat.id] = {'state': ASK_NAME}
        else:
            show_user_panel(message)

def ask_name(message):
    # Initialize user data if it doesn't exist
    if message.chat.id not in user_states:
        user_states[message.chat.id] = {}

    # Store the name and timestamp in user data
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_states[message.chat.id]['state'] = ASK_CONTACT
    ask_contact(message)  # Directly call ask_contact to prompt for contact

def ask_contact(message):
    if message.chat.id not in user_states:
        user_states[message.chat.id] = {}
    if user_states[message.chat.id].get('state') == ASK_CONTACT and 'contact' not in user_states[message.chat.id]:
        contact_button = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        contact_button.add(types.KeyboardButton("Kontaktni yuborish 📞", request_contact=True))
        bot.send_message(message.chat.id, "Iltimos, kontakt ma'lumotlaringizni yuboring: 📱", reply_markup=contact_button)
    else:
        show_user_panel(message)

def show_user_panel(message):
    user_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    referral_button = types.KeyboardButton("Referal linkni olish 🔗")
    referral_count_button = types.KeyboardButton("Referal qo'shilganlar soni 📈")
    user_keyboard.add(referral_button)
    user_keyboard.add(referral_count_button)
    bot.send_message(message.chat.id, "Foydalanuvchi paneliga xush kelibsiz. Quyidagi tugmalardan foydalaning: 👇", reply_markup=user_keyboard)
    
    inline_keyboard = types.InlineKeyboardMarkup()
    video_button = types.InlineKeyboardButton("Masterklassga qo'shilish 🎥", callback_data='video')
    inline_keyboard.add(video_button)
    bot.send_message(message.chat.id, "Quyidagi tugmani bosing: 👇", reply_markup=inline_keyboard)
    
    user_states[message.chat.id]['state'] = USER_PANEL

def show_admin_panel(message):
    admin_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    data_button = types.KeyboardButton("Ma'lumotlarni olish 📊")
    set_link_button = types.KeyboardButton("Linkni o'rnatish 🔗")
    send_broadcast_button = types.KeyboardButton("Xabar yuborish 📢")
    admin_keyboard.add(data_button)
    admin_keyboard.add(set_link_button)
    admin_keyboard.add(send_broadcast_button)
    bot.send_message(message.chat.id, "Admin paneliga xush kelibsiz. Quyidagi tugmalardan foydalaning: 👇", reply_markup=admin_keyboard)
    user_states[message.chat.id] = {'state': ADMIN_PANEL}

@bot.callback_query_handler(func=lambda call: True)
def button(call):
    if call.data == 'video':
        if video_link:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Masterklassga qo'shilish uchun kanalga yo'naltirilasiz: {video_link} 🎥")
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Link hali o'rnatilmagan. ❌")
    elif call.data == 'referral':
        referral_link = generate_referral_link(call.message.chat.id)
        referral_data[call.message.chat.id] = {
            'referral_link': referral_link,
            'referrer': None,
            'count': 0,
            'points': 0
        }
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Sizning referal linkingiz: {referral_link} 🔗")

@bot.message_handler(func=lambda message: message.text == "Ma'lumotlarni olish 📊" and is_admin(message.from_user.id))
def handle_get_data(message):
    save_data_to_excel()
    with open('user_data.xlsx', 'rb') as file:
        bot.send_document(message.chat.id, file)

@bot.message_handler(func=lambda message: message.text == "Linkni o'rnatish 🔗" and is_admin(message.from_user.id))
def handle_set_video_link_prompt(message):
    bot.send_message(message.chat.id, "Iltimos, linkni kiriting: ✍️")
    user_states[message.chat.id] = {'state': SET_VIDEO_LINK}

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == SET_VIDEO_LINK and is_admin(message.from_user.id))
def handle_set_video_link(message):
    global video_link
    video_link = message.text
    bot.send_message(message.chat.id, f"Link o'rnatildi: {video_link} ✅")
    user_states[message.chat.id]['state'] = ADMIN_PANEL  # Return to admin panel after setting video link

@bot.message_handler(func=lambda message: message.text == "Xabar yuborish 📢" and is_admin(message.from_user.id))
def handle_send_broadcast_prompt(message):
    bot.send_message(message.chat.id, "Iltimos, yuboriladigan xabarni kiriting: ✍️")
    user_states[message.chat.id] = {'state': SEND_BROADCAST}

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == SEND_BROADCAST and is_admin(message.from_user.id), content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_send_broadcast(message):
    if message.content_type == 'text':
        broadcast_message = message.text
        user_states[message.chat.id]['broadcast_message'] = broadcast_message
    elif message.content_type == 'photo':
        user_states[message.chat.id]['broadcast_message'] = {'type': 'photo', 'file_id': message.photo[-1].file_id, 'caption': message.caption}
    elif message.content_type == 'video':
        user_states[message.chat.id]['broadcast_message'] = {'type': 'video', 'file_id': message.video.file_id, 'caption': message.caption}
    elif message.content_type == 'document':
        user_states[message.chat.id]['broadcast_message'] = {'type': 'document', 'file_id': message.document.file_id, 'caption': message.caption}
    elif message.content_type == 'voice':
        user_states[message.chat.id]['broadcast_message'] = {'type': 'voice', 'file_id': message.voice.file_id, 'caption': message.caption}
    
    confirm_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    confirm_button = types.KeyboardButton("Tasdiqlash ✅")
    cancel_button = types.KeyboardButton("Bekor qilish ❌")
    confirm_keyboard.add(confirm_button, cancel_button)
    bot.send_message(message.chat.id, "Xabarni tasdiqlaysizmi?", reply_markup=confirm_keyboard)
    user_states[message.chat.id]['state'] = CONFIRM_BROADCAST

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == CONFIRM_BROADCAST and is_admin(message.from_user.id))
def handle_confirm_broadcast(message):
    if message.text == "Tasdiqlash ✅":
        broadcast_message = user_states[message.chat.id]['broadcast_message']
        if isinstance(broadcast_message, str):
            for chat_id in all_chat_ids:
                bot.send_message(chat_id, broadcast_message)
        else:
            for chat_id in all_chat_ids:
                if broadcast_message['type'] == 'photo':
                    bot.send_photo(chat_id, broadcast_message['file_id'], caption=broadcast_message['caption'])
                elif broadcast_message['type'] == 'video':
                    bot.send_video(chat_id, broadcast_message['file_id'], caption=broadcast_message['caption'])
                elif broadcast_message['type'] == 'document':
                    bot.send_document(chat_id, broadcast_message['file_id'], caption=broadcast_message['caption'])
                elif broadcast_message['type'] == 'voice':
                    bot.send_voice(chat_id, broadcast_message['file_id'], caption=broadcast_message['caption'])
        bot.send_message(message.chat.id, "Xabar barcha foydalanuvchilarga yuborildi. ✅")
    else:
        bot.send_message(message.chat.id, "Xabar yuborish bekor qilindi. ❌")
    
    # Remove confirmation and cancel buttons
    bot.send_message(message.chat.id, "Admin paneliga qaytdingiz. 👇", reply_markup=types.ReplyKeyboardRemove())
    show_admin_panel(message)  # Return to admin panel after confirmation



@bot.message_handler(func=lambda message: is_admin(message.from_user.id))
def handle_admin_message(message):
    show_admin_panel(message)  # Ensure admin panel is always shown

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == USER_PANEL)
def handle_user_panel(message):
    if message.text == "Masterklassga qo'shilish 🎥":
        if video_link:
            bot.send_message(message.chat.id, f"Masterklassga qo'shilish uchun kanalga yo'naltirilasiz: {video_link} 🎥")
        else:
            bot.send_message(message.chat.id, "Masterklassga qo'shilish uchun link hali o'rnatilmagan. ❌")
    elif message.text == "Referal linkni olish 🔗":
        referral_link = generate_referral_link(message.chat.id)
        referral_data[message.chat.id] = {
            'referral_link': referral_link,
            'referrer': None,
            'count': 0,
            'points': 0
        }
        bot.send_message(message.chat.id, f"Sizning referal linkingiz: {referral_link} 🔗")
    elif message.text == "Referal qo'shilganlar soni 📈":
        count = referral_data.get(message.chat.id, {}).get('count', 0)
        discount = 0
        for c, d in sorted(referral_discounts.items()):
            if count >= c:
                discount = d
            else:
                break
        bot.send_message(message.chat.id, f"Sizning referal linkingiz orqali qo'shilganlar soni: {count}")

def cancel(message):
    bot.send_message(message.chat.id, "Botdan foydalanish bekor qilindi. ❌")
    user_states.pop(message.chat.id, None)

@bot.message_handler(commands=['start'])
def handle_start(message):
    start(message)
    if is_admin(message.from_user.id):
        show_admin_panel(message)  # Show admin panel on start for admins

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == ASK_NAME)
def handle_ask_name(message):
    ask_name(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == ASK_CONTACT, content_types=['contact'])
def handle_ask_contact(message):
    if message.contact:
        user_states[message.chat.id]['contact'] = message.contact.phone_number
        bot.send_message(message.chat.id, "Kontaktingiz qabul qilindi. ✅")
    else:
        bot.send_message(message.chat.id, "Kontakt yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring. ❌")
    ask_contact(message)

@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    cancel(message)

def main():
    bot.polling(none_stop=True, timeout=3)  # Zarur bo'lsa, timeoutni sozlang

if __name__ == '__main__':
    main()