import sys, pytz, glob, importlib, os, logging, logging.config, asyncio
from pathlib import Path
from pyrogram import idle
from aiohttp import web
from datetime import date, datetime
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script 
from plugins import web_server
from lazybot import LazyPrincessBot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

ppath = "plugins/*.py"
files = glob.glob(ppath)
LazyPrincessBot.start()

async def auto_restart():
    """Function to restart the bot every 6 hours."""
    while True:
        await asyncio.sleep(3 * 80 * 90)  # Sleep for 6 hours
        logging.info("Restarting bot automatically after 6 hours...")
        os.execl(sys.executable, sys.executable, *sys.argv)  # Restart the bot

async def Lazy_start():
    print('\n')
    print('Initializing Lazy Bot')
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Lazy Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username
    logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await LazyPrincessBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time, temp.U_NAME))
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()  # Keeps the bot alive and running

async def shutdown(loop):
    """Graceful shutdown to wait for tasks to finish."""
    tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
    if tasks:
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        # Use asyncio.run() to ensure proper event loop handling
        loop = asyncio.get_event_loop()

        # Start the bot and auto-restart task concurrently
        loop.create_task(auto_restart())  # Schedule the auto-restart function
        loop.run_until_complete(Lazy_start())
        
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')