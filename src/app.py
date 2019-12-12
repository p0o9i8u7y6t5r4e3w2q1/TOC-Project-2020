# -*- coding: utf-8 -*-

import os
import sys

from flask import Flask, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FollowEvent, PostbackEvent
from chat.chatmachine import chatmachine
from chat.chatmodel import ChatModel
from utils.bot_msg import MsgBuilder, ActionBuilder
from utils.send_msg import send_message
from database import Database
import pendulum

load_dotenv()
DB = Database.get_instance()
machine = chatmachine
app = Flask(__name__, static_url_path="/img")
hostname = os.getenv("HOST_NAME", None)
# hostname = 'https://panda-transport.herokuapp.com/'

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
default_error_msg = MsgBuilder.text("不明白您的意思")
unkown_error_msg = MsgBuilder.buttons(
    "無效操作，要回到選項嗎?",
    actions=[ActionBuilder.postback("回到選項", "to_choices", "回到選項")])


@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
    message = event.message
    if not isinstance(message, TextMessage):
        send_message(event.reply_token, default_error_msg)
    else:
        model = ChatModel(machine, event)
        if model.check_cancel():
            model.cancel()
        elif model.state == 'user':
            model.show_choices()
        else:
            model.move()
    model.save_user()
    model.destory()


@handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    print(event.__dict__)
    model = ChatModel(machine, event)
    model.show_choices()
    model.save_user()
    model.destory()


@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    print(event.__dict__)
    action = event.postback.data
    print(action)
    if (action == 'show-fsm'):
        handle_show_fsm(event)
        return

    model = ChatModel(machine, event)
    try:
        # function action function
        func = getattr(model, action)
        func()
        model.save_user()
    except:
        model.send_message(unkown_error_msg)
    model.destory()


@handler.default()
def handle_default(event):
    print(event.__dict__)


def handle_show_fsm(event):
    print(event.__dict__)
    model = ChatModel(machine, event)
    timestamp = pendulum.now().int_timestamp
    model.get_graph().draw(f"img/fsm_{timestamp}.png",
                           prog="dot",
                           format="png")
    image_url = f"{hostname}/show-client-fsm?img=fsm_{timestamp}"
    model.send_message(MsgBuilder.image(image_url, image_url))


@app.route("/show-client-fsm", methods=["GET"])
def show_client_fsm():
    img_name = request.args.get('img')
    return send_file(f"../img/{img_name}.png", mimetype="image/png")


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("img/fsm.png", prog="dot", format="png")
    return send_file("../img/fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
