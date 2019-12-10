# -*- coding: utf-8 -*-

import os
from linebot import LineBotApi
from linebot.models import SendMessage

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_message(reply_token, msg: SendMessage):
    print(msg)
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, msg)
