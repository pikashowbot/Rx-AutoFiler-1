import datetime, time, asyncio
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, broadcast_messages_group
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, RPCError
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

        
        
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    BATCH_SIZE = 100  # Number of users processed in each batch
    SEMAPHORE_LIMIT = 50  # Maximum concurrent tasks
    BATCH_DELAY = 2  # Delay in seconds between batches

    # Ask for the broadcast message
    b_msg = await bot.ask(chat_id=message.from_user.id, text="Now Send Me Your Broadcast Message")

    try:
        users = await db.get_all_users()
        sts = await message.reply_text("Broadcasting your messages...")
        start_time = time.time()

        total_users = await db.total_users_count()
        done, blocked, deleted, failed, success = 0, 0, 0, 0, 0

        sem = asyncio.Semaphore(SEMAPHORE_LIMIT)

        async def send_message(user):
            nonlocal success, blocked, deleted, failed, done
            async with sem:
                if "id" not in user:
                    failed += 1
                    done += 1
                    return
                user_id = int(user["id"])
                try:
                    pti, sh = await broadcast_messages(user_id, b_msg)
                    if pti:
                        success += 1
                    elif sh == "Blocked":
                        blocked += 1
                    elif sh == "Deleted":
                        deleted += 1
                    elif sh == "Error":
                        failed += 1
                except Exception as e:
                    print(f"Unexpected error for user {user_id}: {e}")
                    failed += 1
                finally:
                    done += 1

        batch_tasks = []
        batch_count = 0

        async for user in users:
            batch_tasks.append(send_message(user))
            batch_count += 1

            if batch_count >= BATCH_SIZE:
                await asyncio.gather(*batch_tasks)
                batch_tasks = []
                batch_count = 0

                # Live status update
                await sts.edit(
                    f"Broadcast in progress:\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done}/{total_users}\n"
                    f"Success: {success}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}\n"
                    f"Failed: {failed}"
                )
                await asyncio.sleep(BATCH_DELAY)

        # Process any remaining users
        if batch_tasks:
            await asyncio.gather(*batch_tasks)

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(
            f"Broadcast Completed:\n\n"
            f"Time Taken: {time_taken}\n"
            f"Total Users: {total_users}\n"
            f"Completed: {done}/{total_users}\n"
            f"Success: {success}\n"
            f"Blocked: {blocked}\n"
            f"Deleted: {deleted}\n"
            f"Failed: {failed}"
        )
    except Exception as e:
        print(f"Broadcasting error: {e}")
        
              
                                  
@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    b_msg = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Broadcast Message")
    groups = await db.get_all_chats()
    sts = await message.reply_text(
        text='Broadcasting your messages To Groups...'
    )
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = 0

    success = 0
    async for group in groups:
        pti, sh = await broadcast_messages_group(int(group['id']), b_msg)
        if pti:
            success += 1
        elif sh == "Error":
                failed += 1
        done += 1
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")
        