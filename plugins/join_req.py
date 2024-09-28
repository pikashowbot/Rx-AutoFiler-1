from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, SECOND_AUTH_CHANNEL, THIRD_AUTH_CHANNEL
from utils import temp, is_subscribed

FSUB_CHANNELS = [AUTH_CHANNEL, SECOND_AUTH_CHANNEL, THIRD_AUTH_CHANNEL]

@Client.on_chat_join_request(filters.group | filters.channel)
async def autoapprove(client: Client, message: ChatJoinRequest):
    user = message.from_user
    if not await db.check_join_request(user.id, message.chat.id):
        await db.add_join_request(user.id, message.chat.id) 
        
    all_joined = True
    for channel_id in FSUB_CHANNELS:
        if not await is_subscribed(client, message, [channel_id]):
            all_joined = False
            break
    if all_joined:
        dl = temp.DEL_MSG.get(user.id)
        if dl:
            await dl.delete()


@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.delete_all_join_requests()    
    await message.reply("ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ")



