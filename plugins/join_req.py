from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, SECOND_AUTH_CHANNEL, THIRD_AUTH_CHANNEL

@Client.on_chat_join_request(filters.chat(SECOND_AUTH_CHANNEL))
async def join_reqs2(client, message: ChatJoinRequest):
    if not await db.find_join_req2(message.from_user.id):
        await db.add_join_req2(message.from_user.id)
    
@Client.on_chat_join_request(filters.chat(THIRD_AUTH_CHANNEL))
async def join_reqs3(client, message: ChatJoinRequest):
    if not await db.find_join_req3(message.from_user.id):
        await db.add_join_req3(message.from_user.id)

@Client.on_message(filters.command("delreq2") & filters.private & filters.user(ADMINS))
async def del_requests2(client, message):
    await db.del_join_req2()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ 2nd ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")

@Client.on_message(filters.command("delreq3") & filters.private & filters.user(ADMINS))
async def del_requests3(client, message):
    await db.del_join_req3()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ 3rd ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")