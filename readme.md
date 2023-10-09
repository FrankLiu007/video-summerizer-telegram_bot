# Video Summerizer & Telegram Bot (currently only supports YouTube)
[中文readme](readme_cn.md)
## !!! Attension: English readme is translated from the Chinese version using chatgpt!
## Why?
I have favorite video content creators, but some of them are very prolific, making it time-consuming to watch all their videos. That's why I created this video summarization project and push the summarized content to a Telegram bot.

# Video Summerizer (currently only supports YouTube)

## Project Main Components:
> Frontend
1. Telegram bot: Responsible for adding video channels and deleting video channels.

> Backend
Principle:
- For videos with subtitles, download them directly.
- For videos without subtitles, download the audio part (YouTube separates audio and video).
- Use faster_whisper to convert audio to subtitles.
- Summarize subtitle content using GPT.

# Video Summerizer (currently only supports YouTube)

- For videos with subtitles, download them directly.
- For videos without subtitles, download the audio part (YouTube separates audio and video).
- Use faster_whisper to convert audio to subtitles.
- Summarize subtitle content using GPT.

## To-Do
- [x] Add support for a database (consider using sqlite3). The program should maintain a database connection object at all times.
- [x] Implement a single config file that contains all required parameters.
- [ ] Add two menu options to the Telegram bot: (1) Add Video and (2) Delete Video. Its main purpose is to add temporarily desired videos.
- [x] Monitor changes in subscriptions and process messages in the background. After processing, send them to users.
  - Ideally, check the channel every hour for new videos using rsshub to fetch content. Consider hashing rsshub content and storing the latest hash; if the hash changes, it indicates new content. Alternatively, check the release time of the latest video to determine if there are updates.
- [ ] Merge `run_bot` and `run_summerizer` into a single thread. Reason: The bot has limited functionality and infrequent use, so combining them as a coroutine should not pose significant issues.
- [x] Address the possibility of `run_bot` crashing by using async aiosqlite.
- [x] Improve `readme.md`. Consider an elegant way to avoid uploading sensitive information to Git, such as using environment variables. Provide an external configuration file during testing, while including only examples in the project.
- [ ] Download audio to a specified "download" directory and make it configurable.
- [ ] Refactor `openai_api.py` to improve code structure. Consider using `openai_helper.py` as a replacement.
- [x] For long videos, reviewing subtitles is time-consuming. Subtitles need to be organized (edited and divided into paragraphs) and then converted into articles.
- [ ] For some popular videos, save subtitles and organized documents for later use. Since all videos are public, privacy concerns do not apply.
- [ ] Add a summary point: Explore the various components of a video's title and verify which information from the video confirms the title's claims.
- [ ] Implement error handling for HTTP requests.
- [ ] Consider standardizing proxy settings for HTTP requests.
- [ ] Allow access to specified users only (due to limited GPU resources).

## Run
```python
python src/run_bot.py
python src/run_summarizer.py

## Install  (not finished)
> 1. install pytorch
> 2. install faster-whisper
> 3. install ytd-nightly (git clone  https://github.com/ytdl-org/ytdl-nightly#installation )
> 4. 
