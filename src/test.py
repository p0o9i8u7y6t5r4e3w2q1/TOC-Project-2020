# -*- coding: utf-8 -*-

from dotmap import DotMap
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from chat.chatmachine import chatmachine
from chat.chatmodel import ChatModel
from database import Database

DB = Database.get_instance()
machine = chatmachine
event = DotMap({'source': {'user_id': "user1235"}, 'message': {'text': '新竹'}})

model = ChatModel(machine, event)
getattr(model, 'to_choices')()
model.print_state()
"""
print(model.user.__dict__)
model.get_graph().draw("img/fsm.png", prog="dot", format="png")

model.show_choices()
print(model.user.__dict__)
model.print_state()
model.action()
model.get_graph().draw("img/fsm.png", prog="dot", format="png")
model.move()
# model.save_user()
"""
