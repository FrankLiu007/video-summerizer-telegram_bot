import requests
from db_query import *
import time
from youtube2srt import audio2text, SubtitleDownloader
from OpenaiApi import SrtSummarizer
import asyncio
import json

def send_telegram_message(token, chat_id, message, proxies):
    """
    给 Telegram 用户发送消息。
    
    :param token: Telegram Bot 的访问 Token。
    :param chat_id: 接收消息的用户 ID。
    :param message: 要发送的消息内容。
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=params, proxies=proxies)
    return response

async def update_video_pool(conn, video_pool, lock):

    print("Running update_video_pool")
    all_channels=await select_data_from_database(conn, "user_channel")
    print("all_channels: ")
    for channel in all_channels:
        print("processing channel: ", channel["channel_name"])
        videos=await get_video_list(conn, channel) 
        if videos:
            async with lock:
                if channel['channel_url'] in video_pool:
                    video_pool[channel['channel_url'] ].extend(videos)
                else:
                    video_pool[channel['channel_url'] ]= videos
    return

async def get_video_list(conn, channel):
    
    user=await select_data_from_database(conn, "user_channel", tg_user_id=channel["tg_user_id"], channel_url=channel["channel_url"])
    user=user[0]

    old_video_time=user["newest_video_time"]
    now=time.time()+time.altzone

    res=requests.get("https://rsshub.app/"+channel["channel_url"]+".json")
    data=json.loads(res.text)
    
    result=[]
    for item in data["items"] :

        pubDate=item["date_published"]
        time_tuple = time.strptime(pubDate, "%Y-%m-%dT%H:%M:%S.%fZ")
        t1 = time.mktime(time_tuple)
        
        if t1<=old_video_time:  # only process video published after last processed video
            break
        if now-t1>3600*24:  # only process video published in 1 day
            break
        print(f"channel {channel['channel_name']}: ",f'New video {item["title"]} found, adding to video pool!' )
        result.append({"title":item["title"], "link":item["url"], "pubDate":t1, "tg_user_id":channel["tg_user_id"]})  # use timestamp as pubDate

    return result

def video_pool_is_empty(video_pool):
    x=False
    for channel in video_pool:
        x=x or video_pool[channel]
    return not x

async def video_summerizer(conn, config, video_pool, lock):

    model=config['faster_whisper']['model']  #default large-v2
    gpu=config['faster_whisper']['gpu_index']
    audio2text_tool=audio2text(model, gpu)  ## support gpu only, cpu too slow

    # 创建字幕下载器实例
    downloader = SubtitleDownloader(config['youtube_dl'], audio2text_tool)
    srt_summarize = SrtSummarizer(config["openai"]["key"], config["openai"]["prompt"] ,config["proxies"],  config["openai"]["model"]   , config["openai"]["max_tokens"]  )

    if not video_pool:
        await asyncio.sleep(20) # sleep 20 seconds if video pool is empty
    if video_pool_is_empty(video_pool):
        print("video pool is empty!")
        await asyncio.sleep(60*60) # sleep 1 hour if video pool is empty

    for channel in video_pool:
        print(f"start summerize channel {channel}")
        if not video_pool[channel]:
            print(f"video pool for channel {channel} is empty!")
            continue
        user_channel=await select_data_from_database(conn, "user_channel", channel_url=channel, tg_user_id=video_pool[channel][0]["tg_user_id"])
        
        old_video_time=user_channel[0]["newest_video_time"]

        new_video_time=-1

        while video_pool[channel]:
            async with lock:                   
                video=video_pool[channel].pop(0)

            if video["pubDate"] <= old_video_time:
                print('Error: video pubDate is older than newest_time, skip this channel. This is not supposed to happen, please check the code!')
                break
            if video["pubDate"] > new_video_time:
                new_video_time=video["pubDate"]

            srt=downloader.get_subtitles( video["link"] )
            result=srt_summarize.summarize(srt)
            if result is not None:
                
                res=send_telegram_message(config["telegram_bot"]["token"], video["tg_user_id"], result, config["proxies"])
                if res.status_code!=200:
                    print(f"Error: telegram message sent failed! status_code={res.status_code}, text={res.text}")
                    continue
                else:
                    print(f"video {video['title']} summerized and sent to user {video['tg_user_id']}!")

        if new_video_time>0:
            await update_data_to_database(conn, "user_channel", {"newest_video_time": new_video_time}, {"tg_user_id":video["tg_user_id"], "channel_url":channel})


async def main():
    import aiosqlite
    import json
    import sqlite3
    import time
    import asyncio
    lock = asyncio.Lock()

    path="config.json"
    with open(path, 'r') as f:
        config=json.load(f)
    video_pool={}
    async with aiosqlite.connect(config['db_path']) as conn:

        conn.row_factory = sqlite3.Row  ## return dict instead of tuple
        await update_video_pool(conn,  video_pool, lock) 
    print(video_pool)

if __name__ == "__main__":
    asyncio.run(main())