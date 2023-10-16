from telegram_bot import Bot
import json

import os
import chardet
if __name__ == "__main__":

    path="../video-summerizer-config.json"
# read config file with encoding detection
    with open(path, 'rb') as f:
        data = f.read()
    encoding = chardet.detect(data)['encoding']
    data = data.decode(encoding)
    config = json.loads(data)
    os.environ["HTTP_PROXY"] = config["proxies"]["http"]
    os.environ["HTTPS_PROXY"] = config["proxies"]["https"]
    bot=Bot(config["telegram_bot"]['token'], config["db_path"])

    bot.run()