# -*- coding: utf-8 -*-

from typing import Dict, List

from dotmap import DotMap
from linebot.models import SendMessage, Event
from transitions.extensions import HierarchicalGraphMachine as Machine
from transitions.extensions.nesting import NestedState

from utils.machine import MessageState, Transition
from utils.send_msg import send_message

from utils.bot_msg import ActionBuilder, MsgBuilder
from .conversations import Conversation, conversation, AppConversations as Cs
from .questions import Question
from database import Database, User

NestedState.separator = '.'


class ChatMachine(Machine):
    USER = 'user'
    CHOICES = 'choices'

    def __init__(self, conversations: List[Conversation]):
        super().__init__(self,
                         states=[
                             NestedState(self.USER, on_enter="on_user"),
                             MessageState(self.make_choices_msg(conversations),
                                          name=self.CHOICES,
                                          on_enter="on_choices"),
                             *self.make_states(conversations)
                         ],
                         initial=self.USER,
                         show_conditions=True,
                         ignore_invalid_triggers=True)
        self.conversations = conversations
        self.add_transitions(self.make_transitions(conversations))

    @classmethod
    def make_states(cls, conversations: List[Conversation]):
        states = list()
        for idx, c in enumerate(conversations, start=1):
            c.name = f"a{idx}-{c.name}"  # avoid same name
            states.append(c.toNestedState(cls.USER))
        return states

    @classmethod
    def make_transitions(cls,
                         conversations: List[Conversation]) -> List[DotMap]:
        transitions: List[DotMap] = list()
        transitions.append(Transition("show_choices", cls.USER, cls.CHOICES))
        for c in conversations:
            transitions.append(Transition(c.trigger, cls.CHOICES, c.name))
        return transitions

    def make_choices_msg(self,
                         conversations: List[Conversation]) -> SendMessage:
        actions = list()
        actions.append(
            ActionBuilder.postback(label='查看fsm',
                                   display_text='查看fsm',
                                   data='show-fsm'))
        for idx, c in enumerate(conversations):
            actions.append(
                ActionBuilder.postback(label=c.text,
                                       display_text=c.text,
                                       data=c.trigger))
        return MsgBuilder.buttons(u"需要什麼服務?", actions=actions)


chatmachine = ChatMachine([Cs.QUERY_NOW_TRAIN_INFO, Cs.QUERY_METRO_WAITING_INFO])
