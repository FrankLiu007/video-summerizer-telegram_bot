
import json
from summerizer import update_video_pool, video_summerizer
import asyncio
import time

from db_query import *
import aiosqlite

# def send_telegram_message(token, chat_id, message, proxies):
#     """
#     给 Telegram 用户发送消息。
    
#     :param token: Telegram Bot 的访问 Token。
#     :param chat_id: 接收消息的用户 ID。
#     :param message: 要发送的消息内容。
#     """
#     url = f"https://api.telegram.org/bot{token}/sendMessage"
#     params = {"chat_id": chat_id, "text": message}
#     response = requests.post(url, data=params, proxies=proxies)
#     return response

async def init_db(db_path):
    db=await aiosqlite.connect(config['db_path']) 
    db.row_factory = aiosqlite.Row  ## return dict instead of tuple
    return db

async def video_pool_update_task(t, config, video_pool, lock):
    print("Running video_pool_update_task")
    async with aiosqlite.connect(config['db_path']) as conn:
        conn.row_factory = aiosqlite.Row  ## return dict instead of tuple

        while True:
            t0=time.time()
            print("start video_pool_update_task")
            await update_video_pool(conn,  video_pool, lock)  
            if time.time()-t0>t:
                print(f"Warning: video pool task takes too long time, longer than timer interval {t} seconds")
                print("This should never happen, because summerizer always works slower than the video pool update task!")
            await asyncio.sleep(t)

async def video_summerizer_task(config, video_pool, lock):
    print("Running summerizer task")

    async with aiosqlite.connect(config['db_path']) as conn:
        conn.row_factory = aiosqlite.Row  ## return dict instead of tuple
        while True:
            if not video_pool:
                await asyncio.sleep(20) # sleep 20 seconds if video pool is empty
            await video_summerizer(conn, config, video_pool, lock)

async def main():

    lock = asyncio.Lock()

    path="../video-summerizer-config.json"
    with open(path, 'r') as f:
        config=json.load(f)

    video_pool={} 

    #1. video pool update task
    task0=asyncio.create_task( video_pool_update_task(60*30 ,config, video_pool, lock) ) # update video pool every half hour

    task1= asyncio.create_task(video_summerizer_task( config, video_pool, lock) )
 
    await asyncio.gather(task0, task1)


if __name__ == "__main__":
    asyncio.run(main())







