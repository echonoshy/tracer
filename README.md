# Tracer 猎空

> Tracer（猎空）是可以进行时间跳跃的冒险家。拥有双手枪快速连射、能量强大的脉冲炸弹与如珠般的幽默话语，猎空在伸张正义时能快速穿越空间并闪回时间。

—— From [OverWatch](https://ow.blizzard.cn/heroes/tracer)  
<img src="https://upload.wikimedia.org/wikipedia/zh/d/d6/Tracer_Overwatch.png" width="200" height="200" />


## 📋 项目简介

> [!WARNING]
> 由于 Gewechat 停止维护，相关服务已经被微信修复，后续模拟登陆服务可能无法正常使用。

Tracer: 是一个提供微信群组自动化信息服务的llm-workflow工具，支持群内资讯推送、任务提醒及公告发布等。

当前功能：订阅 Github trending 榜单 🌟，并且使用 deepseek-r1 进行知识总结，并使用微信自动化推送到指定的微信群 📱。
因为不太想过分打扰微信群友，暂时只准备做 Github 这单一功能。但并不是这个项目的极限，比如打造自己的金融讯息管家等，基础功能都已经实现了，想象力才是这个项目的天花板。

[![视频介绍](https://img.shields.io/badge/点击观看-B站视频-blue?logo=bilibili)](https://www.bilibili.com/video/BV15GXQY3Ez3/?vd_source=2acabf9b10c0b70274da02f31cf31368)

## 🔧 安装

### 系统要求和注意事项

1. 系统环境推荐：CentOS或Ubuntu，Windows系统可能出现未知错误
2. 由于容器需要用到2531和2532端口，要保证服务器这两个端口没有被占用
3. 容器启动后会访问腾讯服务，因此要保证服务器能够访问外网，并且出网没有被限制，否则会导致容器无法正常启动
4. 使用者必须搭建服务到同省服务器或者电脑里方可正常使用

### 部署步骤

先在项目根目录安装 Python 依赖，并从模板创建本地配置。

```sh
python -m pip install -r requirements.txt
cp -n .env-sample .env
```

1. 部署 Gewechat 服务
```sh
# 拉镜像 
docker pull registry.cn-hangzhou.aliyuncs.com/gewe/gewe:latest
docker tag registry.cn-hangzhou.aliyuncs.com/gewe/gewe gewe

# 启动镜像 
mkdir -p /root/temp
docker run -itd -v /root/temp:/root/temp -p 2531:2531 -p 2532:2532 --privileged=true --name=gewe gewe /usr/sbin/init
```

2. 验证微信并登陆 🔐
```python
# 依次执行workflow下的initialize.py, login。
python workflows/initialize.py  # 获取token，app_id(登陆设备id)

# 将上一步获取到的token和app_id保存到.env文件中 (参考.env-sample)
python workflows/login.py  # 执行并扫码登录
# 如要发送一条测试消息，明确指定接收人的微信 ID
# python workflows/login.py --test-recipient wxid_xxx
```

## ▶️ 启动

```python
# 补充完整剩下的.env配置， 执行单轮测试 ✅
python workflows/post_group_message.py
```

```sh
# 设置定时任务 ⏰
mkdir -p logs/ && touch logs/github_daily.log

crontab -i
# 在定时器编辑器中复制下面内容，注意路径需要和你自己的机器匹配 ⚠️
45 8 * * * cd /home/ubuntu/tracer && /home/ubuntu/miniconda3/bin/python workflows/post_group_message.py >> /home/ubuntu/tracer/logs/github_daily.log 2>&1
```


## 致谢
- [Gewechat](https://github.com/Devo919/Gewechat) 
- [gewechat-python](https://github.com/hanfangyuan4396/gewechat-python)  
- [OpenGithubs](https://github.com/OpenGithubs/github-daily-rank)
