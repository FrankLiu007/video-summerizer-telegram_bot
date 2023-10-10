from telegram_bot import Bot
import json

import sqlite3
import aiosqlite
import asyncio
import os
if __name__ == "__main__":
    path="../video-summerizer-config.json"
    with open(path, 'r') as f:
        config=json.load(f)
    os.environ["HTTP_PROXY"] = config["proxies"]["http"]
    os.environ["HTTPS_PROXY"] = config["proxies"]["https"]
    bot=Bot(config["telegram_bot"]['token'], config["db_path"])

    bot.run()