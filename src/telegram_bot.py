import logging

from telegram import __version__ as TG_VER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove,  BotCommand
import  asyncio
import pytube
from db_query import *
import time
import aiosqlite
import os

from telegram import __version_info__
if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



async def add_user_if_not_exist(conn, user_id, username):

    user=await select_data_from_database(conn, "user", tg_user_id=user_id)
    if not user:
        now=time.time()+time.altzone
        print("user not exists, adding user: ",  username)
        await insert_data_to_database(conn, "user", tg_user_id = user_id, username=username, last_processed_video_time=now)
    return 

class Bot:

    async def init_db(self, db_path):       
        self.conn = await aiosqlite.connect(db_path)
        self.conn.row_factory = aiosqlite.Row  ## return dict instead of tuple

    async def set_menu(self):
        commands = [
            BotCommand(command='/add_channel', description='添加频道'),
            BotCommand(command='/view_channel', description='查看频道列表'),
            BotCommand(command='/remove_channel', description='删除频道'),
            BotCommand(command='/readme', description='Read me')
        ]
        await self.application.bot.setMyCommands(commands)
            
    def add_handlers(self):
        self.application.add_handler(CommandHandler("add_channel", self.add_channel))
        self.application.add_handler(MessageHandler( filters.TEXT & ~filters.COMMAND, self.message_handler) )
        self.application.add_handler(CommandHandler("readme", self.readme))
        self.application.add_handler(CommandHandler("view_channel", self.view_channel))
        self.application.add_handler(CommandHandler("remove_channel", self.remove_channel))
        self.application.add_handler(CallbackQueryHandler(self.remove_channel_callback))

    def __init__(self, bot_token, db_path) -> None:
        builder=ApplicationBuilder().token(bot_token)
        self.application = builder.build()
        loop= asyncio.get_event_loop()
        loop.run_until_complete(self.init_db(db_path))

        loop.run_until_complete(self.set_menu())
        self.add_handlers()

    async def readme(self, update: Update, context: CallbackContext) ->None:
        tt="""
    This bot is a video summerizer. 
    It will try to get all the newest video in the channel list (only youtube channel at present) and then try to generate subtitles and then summerize the subtitles using chatgpt.
    It will help you get the main idea of the video without watching the video.
    The bot is still under development, so it may not work properly.
        
    """
        await update.message.reply_text(tt)
        return


    async def add_channel(self, update: Update, context: CallbackContext) -> None:
        """Adds a channel to the list of channels the bot is in"""
        user_id = update.effective_user.id
        username = update.effective_user.full_name

        print("adding channel for ", username)

        await add_user_if_not_exist(self.conn, user_id, username)

        context.user_data['action']='add_channel'

        await update.message.reply_text(f"please input the url of a video, the bot will detect the channel automaticly:")

    async def view_channel(self, update: Update, context: CallbackContext) -> None:
        """Adds a channel to the list of channels the bot is in"""
        user_id = update.effective_user.id
        username = update.effective_user.full_name
        await add_user_if_not_exist(self.conn, user_id, username)

        print("view channel for ", username)

        #all_channel=get_all_channel(self.cur, user_id)
        all_channel= await select_data_from_database(self.conn, "user_channel", tg_user_id=user_id)

        context.user_data['action']='view_channel'
        
        if not all_channel:
            await update.message.reply_text('no channel added yet')
        else:
            tt='all channels:\n'
            for index, item in enumerate(all_channel):
                tt=tt + str(index+1)+". " + item['channel_name'] + '\n'
            await update.message.reply_text(tt)

        return

    async def remove_channel_callback(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        username = update.effective_user.full_name
        await add_user_if_not_exist(self.conn, user_id, username)

        print("remove channel for ", username)
        
        query = update.callback_query
        await query.answer()
        channel=await select_data_from_database(self.conn, "user_channel", tg_user_id=user_id, channel_url=query.data)
        if channel:
            await delete_data_from_database(self.conn, "user_channel", tg_user_id=user_id, channel_url=query.data)
            await query.edit_message_text(text=f'channel:  {channel[0]["channel_name"]} removed!')
        else:
            await query.edit_message_text(text=f'channel not found: {query.data}')
        return

    async def remove_channel(self, update: Update, context: CallbackContext) -> None:

        user_id = update.effective_user.id
        username = update.effective_user.full_name
        await add_user_if_not_exist(self.conn, user_id, username)

        keyboard=[]
        all_channel=await select_data_from_database(self.conn, "user_channel", tg_user_id=user_id)

        for item in all_channel:
            keyboard.append([InlineKeyboardButton(item['channel_name'], callback_data=item['channel_url'])])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Select channel need to remove:\n', reply_markup=reply_markup)

    def get_youtube_channel(self, url):
        proxies={
            "http": os.environ["HTTP_PROXY"],
            "https": os.environ["HTTPS_PROXY"]
        }
        try:
            x=pytube.YouTube(url, proxies=proxies)
            channel_id=x.channel_id
            channel_name=x.author
            return {'url':"youtube/channel/"+channel_id, "name":channel_name, "id":channel_id}
        except:
            print('get channel from ', url, 'failed!')
            return False 

    async def message_handler(self, update: Update, context: CallbackContext) -> None:

        user_id = update.effective_user.id
        username = update.effective_user.full_name
        await add_user_if_not_exist(self.conn,  user_id, username)

        url = update.message.text
        print('user_id ', user_id, 'url', url)

        if context.user_data.get('action') == 'add_channel':
            channel=self.get_youtube_channel(url)
            if  channel:
                ch=await select_data_from_database(self.conn, "user_channel", tg_user_id=user_id, channel_url=channel['url'])
                if ch:   ## channel already exists
                    await update.message.reply_text(f"Channel: {channel['name']} already exists!")
                    return
                else:
                    await insert_data_to_database(self.conn, 'user_channel', tg_user_id=user_id, channel_url=channel['url'], channel_name=channel['name'])
                    await update.message.reply_text(f"Channel: {channel['name']} added!")
                    return
            else:
                await update.message.reply_text(f'{url} is not a valid youtube url!')

        elif context.user_data.get('action') == 'view_channel': # example of using context.user_data to pass data between handlers
            pass

        return              

    def run(self):
        # Run the bot until the user presses Ctrl-C

        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


import threading
import sqlite3
if __name__ == "__main__":
    bot_token='your-bot-token'
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row  ## return dict instead of tuple
    bot=Bot(bot_token, conn)

    bot_thread = threading.Thread(target=bot.run())