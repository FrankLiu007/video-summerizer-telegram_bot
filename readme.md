#  视频 summerizer & Telegram Bot  (only youtube supported at present ) [English Document](readme_en.md) 
## Why?  我有喜欢的视频博主，但是该博主太勤奋，听他的视频非常费时间，因此做了这个视频总结的项目，并将总结的内容推送到telegram bot .

# Video Summerizer (only youtube supported at present )
# 项目主要三部分：
> 前端
1. Telegram bot。前端，负责添加视频频道、删除视频频道
> 后端
原理：
- 对于有字幕的视频，直接下载; 
- 对于没有字幕的视频，则下载视频的音频部分（youtube 是音视频分开的）
- 通过 faster_whisper 将语音转为字幕
- 用 gpt 对字幕内容进行总结

# Video Summerizer (only youtube supported at present )

- 对于有字幕的视频，直接下载; 
- 对于没有字幕的视频，则下载视频的音频部分（youtube 是音视频分开的）
- 通过 faster_whisper 将语音转为字幕
- 用 gpt 对字幕内容进行总结



todo 
- [x] 加入数据库的支持，暂时考虑sqlite3，程序任何时候应该保持一个数据库的连接对象。
- [x] 单个config文件，配置需要的所有参数
- [ ] tg bot 增加2个菜单，功能分别是（1）添加视频 （2）删除视频。它的主要功能是增加临时临时想看的视频）
- [x] 监视订阅的变化，后台处理信息，处理完成后发送给用户。
* 正常应该是，每1个小时 去检查一下channel看是否有新视频，通过rsshub获取内容。可以考虑把rsshub的内容做个hash，并存储最近的一个hash，如果hash变了，表明有新内容了。也可以看最新的视频的发布时间，来确定是否有更新。
- [ ] 将run_bot 和 run_summerizer 合并，合并到一个线程里。理由：bot功能少，使用不频繁，做为一个协程合并，问题不大。
- [x] run_bot可能挂了，sqlite3改成异步的aiosqlite，因此应该挂了。
- [x] ~~完善readme.md, 思考如何优雅的避免敏感信息上传git：用环境变量？~~ 直接外置配置文件，测试时，始终读取外部文件，项目中只给example
- [ ] 音频需要下载到download目录，并且可以配置
- [ ] openai_api.py, 写的不规范，想用openai_helper.py 来替代
- [x] 对于长视频，字幕查看非常费时间，需要将字幕整理（edit 后分段落），然后转成文章。
- [ ] 某些视频，可能看的人多，应该看一次，就把字幕和整理好的文档保存起来，下次不再处理，直接发送给客户，由于都是公开的视频，所有不存在隐私问题。
- [ ] 总结应该加一条：视频的title有几个内容，视频中的哪些信息验证了title的说法。
- [ ] http请求部分的容错处理
- [ ] http请求，proxy的设置的统一化考虑

## Run
    python src/run_bot.py
    python src/run_summerizer.py

## Install  (not finished, I can export conda env, but it may make user confused )
> 1. install pytorch
> 2. install faster-whisper
> 3. install ytd-nightly (git clone  https://github.com/ytdl-org/ytdl-nightly#installation)
> 4. 