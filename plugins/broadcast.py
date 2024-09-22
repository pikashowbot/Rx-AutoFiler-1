from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages_group, broadcast_messages
import asyncio
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, RPCError
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



BATCH_SIZE = 100  # Process 100 users/groups at a time
SEMAPHORE_LIMIT = 50  # Increase concurrent tasks limit
BATCH_DELAY = 1  # Delay in seconds between batches

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )

    start_time = time.time()
    total_users = await db.total_users_count()
    done, blocked, deleted, failed, success = 0, 0, 0, 0, 0

    sem = asyncio.Semaphore(SEMAPHORE_LIMIT)

    async def run_task(user):
        async with sem:
            res = await broadcast_func(user, b_msg)
            return res

    tasks = []
    users_batch = []
    batch_count = 0

    async for user in users:
        users_batch.append(user)
        batch_count += 1

        if batch_count >= BATCH_SIZE:
            tasks.extend([asyncio.ensure_future(run_task(user)) for user in users_batch])
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, tuple):
                    success1, blocked1, deleted1, failed1, done1 = res
                    done += done1
                    blocked += blocked1
                    deleted += deleted1
                    failed += failed1
                    success += success1
                else:
                    print(f"Error: {res}")

            if done % 500 == 0:
                with suppress(Exception):
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

            tasks = []
            users_batch = []
            batch_count = 0
            await asyncio.sleep(BATCH_DELAY)

    if users_batch:  # Process remaining users
        tasks.extend([asyncio.ensure_future(run_task(user)) for user in users_batch])
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, tuple):
                success1, blocked1, deleted1, failed1, done1 = res
                done += done1
                blocked += blocked1
                deleted += deleted1
                failed += failed1
                success += success1
            else:
                print(f"Error: {res}")

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

async def broadcast_func(user, b_msg):
    success, blocked, deleted, failed, done = 0, 0, 0, 0, 0
    try:
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success = 1
        elif pti == False:
            if sh == "Blocked":
                blocked = 1
            elif sh == "Deleted":
                deleted = 1
            elif sh == "Error":
                failed = 1
    except FloodWait as e:
        print(f"FloodWait: Need to wait {e.value} seconds.")
        await asyncio.sleep(e.value)
        return await broadcast_func(user, b_msg)  # Retry after wait
    except RPCError as e:
        print(f"Failed to broadcast to user {user['id']}: {e}")
        failed = 1
    except PeerIdInvalid as e:
        print(f"Invalid peer ID for user {user['id']}: {e}")
        failed = 1
    done = 1
    return success, blocked, deleted, failed, done


        
        
        
@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_group(bot, message):
    groups = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages To Groups...'
    )
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done, failed, success = 0, 0, 0

    async def run_group_task(group):
        try:
            pti, sh = await broadcast_messages_group(int(group['id']), b_msg)
            return pti, sh
        except FloodWait as e:
            print(f"FloodWait: Need to wait {e.value} seconds.")
            await asyncio.sleep(e.value)
            return await run_group_task(group)  # Retry after wait
        except RPCError as e:
            print(f"Failed to broadcast to group {group['id']}: {e}")
            return None, "Error"

    tasks = []
    groups_batch = []
    batch_count = 0

    async for group in groups:
        groups_batch.append(group)
        batch_count += 1

        if batch_count >= BATCH_SIZE:
            tasks.extend([asyncio.ensure_future(run_group_task(group)) for group in groups_batch])
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for pti, sh in results:
                if pti:
                    success += 1
                elif sh == "Error":
                    failed += 1
                done += 1

            if not done % 1000:
                await sts.edit(f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")

            tasks = []
            groups_batch = []
            batch_count = 0
            await asyncio.sleep(BATCH_DELAY)

    if groups_batch:  # Process remaining groups
        tasks.extend([asyncio.ensure_future(run_group_task(group)) for group in groups_batch])
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for pti, sh in results:
            if pti:
                success += 1
            elif sh == "Error":
                failed += 1
            done += 1

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")