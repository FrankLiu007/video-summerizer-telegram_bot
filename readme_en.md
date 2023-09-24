# Video Summerizer  [中文](readme.md)
## (English readme is not always update as it is translated from the chinese document using chatgpt )
Principle: For videos with subtitles, download the subtitles directly; for videos without subtitles, download the audio part of the video (YouTube has separate audio and video), and then use faster_whisper to convert the audio to subtitles. Then summarize the subtitle content using GPT.

# Video Summerizer (only YouTube supported at present)

- For videos with subtitles, download directly.
- For videos without subtitles, download the audio part (YouTube has separate audio and video).
- Convert audio to subtitles using faster_whisper.
- Summarize the subtitle content using GPT.

# Three main parts:
1. Telegram bot. 
2. Voice to text conversion (faster_whisper)
3. Text summarization with GPT, openai_api.py is not written in a standard way, considering replacing with openai_helper.py.

todo 
- [x] Add database support, considering sqlite3 for now. The program should maintain a database connection object at all times.
- [x] A single config file to configure all required parameters.
- [ ] Add two menus to the tg bot, the functions are (1) Add video (2) Delete video. Its main function is to add videos that you temporarily want to watch.
- [x] Monitor subscription changes, process information in the background, and send it to users once processed.
* Normally, check the channel every hour to see if there are new videos, get content through rsshub. Consider hashing the content of rsshub and storing the most recent hash. If the hash changes, it means there's new content. You can also look at the release time of the latest video to determine if there are updates.
- [ ] Merge run_bot and run_summerizer, combine them into one thread. Reason: bot has fewer features, is not used frequently, and merging as a coroutine is not a big issue.
- [x] run_bot might have crashed, sqlite3 changed to asynchronous aiosqlite, so it should have crashed.
- [ ] Improve readme.md, think about how to elegantly avoid uploading sensitive information to git: use environment variables?
- [ ] Audio needs to be downloaded to the download directory and can be configured.
- [ ] 

## Run
    python src/run_bot.py
    python src/run_summerizer.py

## Install  (not finished)
> 1. install pytorch
> 2. install faster-whisper
> 3. install ytd-nightly (git clone  https://github.com/ytdl-org/ytdl-nightly#installation)
> 4. 
