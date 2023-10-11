
import json
from summarizer_helper import update_video_pool, video_summerizer
import asyncio
import time

from db_query import *
import aiosqlite

### 每个任务建一个异步数据库连接更合适（连接数并不多）
# async def init_db(db_path):
#     db=await aiosqlite.connect(config['db_path']) 
#     db.row_factory = aiosqlite.Row  ## return dict instead of tuple
#     return db

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
    import os
    import chardet

    lock = asyncio.Lock()

    path="../video-summerizer-config.json"

# read config file with encoding detection
    with open(path, 'rb') as f:
        data = f.read()
    encoding = chardet.detect(data)['encoding']
    data = data.decode(encoding)
    config = json.loads(data)


    video_pool={} 
    os.environ["HTTP_PROXY"] = config["proxies"]["http"]
    os.environ["HTTPS_PROXY"] = config["proxies"]["https"]
    #1. video pool update task
    task0=asyncio.create_task( video_pool_update_task(60*3 ,config, video_pool, lock) ) # update video pool every half hour

    task1= asyncio.create_task(video_summerizer_task( config, video_pool, lock) )
 
    await asyncio.gather(task0, task1)


if __name__ == "__main__":
    asyncio.run(main())







