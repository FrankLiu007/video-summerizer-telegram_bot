from telegram_bot import Bot
import json
import threading
import sqlite3
import requests
from db_query import *
import lxml.etree as etree



from summerizer_helper import update_summerizer_task_pool



# run video-summerizer in another thread




def run_summerizer(conn):
    from video_summerizer import VideoSummerizer
    summerizer=VideoSummerizer(config)
    summerizer.run()
if __name__ == "__main__":
    path="config.json"
    with open(path, 'r') as f:
        config=json.load(f)

    conn = sqlite3.connect(config['db_path'])
    conn.row_factory = sqlite3.Row  ## return dict instead of tuple

    # 1. run bot in a thread
    bot=Bot(config["telegram_bot"]['token'], conn)
    bot_thread = threading.Thread(target=bot.run)
    bot_thread.start()
    # 2. run a thread to update summerizer_task_pool
    summerizer_task_pool=[]
    task_pool_update_thread=threading.Thread(target=update_summerizer_task_pool, args=(conn,summerizer_task_pool, ))

    # 3. run a thread to run summerizer
    summerizer_thread=threading.Thread(target=run_summerizer, args=(conn, ))