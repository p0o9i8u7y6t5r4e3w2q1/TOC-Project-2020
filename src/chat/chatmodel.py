# -*- coding: utf-8 -*-

from typing import Dict, List

from dotmap import DotMap
from linebot.models import SendMessage, Event
from transitions.extensions import HierarchicalGraphMachine as Machine
from transitions.extensions.nesting import NestedState

from utils.machine import MessageState, Transition
from utils.send_msg import send_message
from utils.bot_msg import ActionBuilder, MsgBuilder

from .conversations import Conversation, conversation
from .questions import Question
from database import Database, User


class ChatModel:
    # trigger functions:
    # lambda_shift
    # move
    # show_choices

    def __init__(self, machine, event: Event):
        user_id = event.source.user_id
        self.event = event
        self.db = Database.get_instance()
        self.machine = machine
        user = self.db.find(user_id)
        if user is None:
            user = User(user_id)
            print(machine)
            machine.push_model(self, initial=machine.initial)
            user.set_state(machine.initial)
        else:
            machine.push_model(self, initial=user.status.state)
        self.user = user

    def on_user(self):
        self.print_state()
        self.save_state()

    def is_answer_valid(self) -> bool:
        self.print_state()
        print(self.is_answer_valid)
        question: Question = self.get_question()
        answer = question.check_answer(self.event)
        if answer is None:
            # call by manual, because hsm not support internal transition in sub hsm (Bug)
            self.halt(question)
            return False
        else:
            self.user.add_answer(answer)
            return True

    def on_question(self):
        print(self.on_question)
        print(self.user.__dict__)
        self.print_state()
        self.save_state()
        question: Question = self.get_question()
        self.send_message(question.question_msg)

    def on_initial(self):  # on conversation start
        print(self.on_initial)
        self.print_state()
        self.user.reset_status(self.state)  # type: ignore
        self.lambda_shift()  # type: ignore

    def on_finish(self):  # on conversation finish
        print(self.on_finish)
        self.print_state()
        self.save_state()
        finish: MessageState = self.get_state()
        print(finish.__dict__)
        self.send_message(finish.message(self))
        self.lambda_shift()  # type: ignore

    def on_choices(self):
        self.print_state()
        self.save_state()
        msg: MessageState = self.get_state()
        self.send_message(msg.message(self))

    # not callback
    def get_state(self):
        return self.machine.get_state(self.state)  # type: ignore

    def check_cancel(self):
        return self.event.message.text == "取消"

    def cancel(self):
        self.to_choices()  # type: ignore

    def get_question(self):
        return self.get_state().obj

    def halt(self, question: Question):  # not call by machine
        print(self.halt)
        self.send_message(question.error_msg)

    def save_user(self):
        self.db.save(self.user)

    def save_state(self):
        self.user.set_state(self.state)  # type: ignore

    def destory(self):
        self.machine.remove_model(self)

    def print_state(self):
        print(f"state: {self.state}")  # type: ignore

    def send_message(self, msg):
        send_message(self.event.reply_token, msg)
        # print(None, msg)

    def get_answer(self):
        return self.user.status.answers
