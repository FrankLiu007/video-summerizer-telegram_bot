from telegram_bot import Bot
import json

import sqlite3
import aiosqlite
import asyncio

if __name__ == "__main__":
    path="../video-summerizer-config.json"
    with open(path, 'r') as f:
        config=json.load(f)
 
    bot=Bot(config["telegram_bot"]['token'], config["db_path"])

    bot.run()