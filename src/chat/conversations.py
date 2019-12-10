# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, List, Optional

from dotmap import DotMap
from linebot.models import Event, SendMessage

from database import User
from transitions import EventData
from transitions.extensions import HierarchicalGraphMachine as Machine
from transitions.extensions.nesting import NestedState
from api.transport_api import THSR
from utils.machine import MessageState, ObjectState, Transition
from utils.bot_msg import MsgBuilder, ActionBuilder
import pendulum

from .questions import Question
from .questions import QuestionBuilder as Qs


class Conversation(Machine):
    INITIAL = 'initial'
    FINISH = 'finish'
    BACK = 'back'

    def __init__(self,
                 questions: List[Question],
                 finish_msg,
                 name: str = 'conversation',
                 text: str = '對話',
                 trigger: str = 'action'):
        states = self.make_states(finish_msg, questions)
        super(Machine, self) \
            .__init__(states=states,
                      initial=self.INITIAL,
                      transitions=self.make_transitions(states),
                      auto_transitions=False,
                      show_conditions=True,
                      name=name)
        # member init
        self.questions: List[Question] = questions
        self.finish_msg: SendMessage = finish_msg
        self.trigger = trigger
        self.text = text

    @classmethod
    def make_states(cls, finish_msg, questions: List[Question]):
        states: List[NestedState] = list()
        states.append(NestedState(cls.BACK))
        if len(questions) == 0:
            states.append(
                MessageState(finish_msg,
                             name=cls.INITIAL,
                             on_enter='on_finish'))
        else:
            states.append(
                MessageState(finish_msg, name=cls.FINISH,
                             on_enter='on_finish'))
            states.append(NestedState(cls.INITIAL, 'on_initial'))
            for idx, q in enumerate(questions, start=1):
                states.append(
                    ObjectState(q,
                                name=f"q{idx}_{q.name}",
                                on_enter='on_question'))
        return states

    @classmethod
    def make_transitions(cls, states: List[ObjectState]) -> List[DotMap]:
        transitions: List[DotMap] = list()
        length = len(states)
        if length == 2:  # default states
            transitions.append(
                Transition('lambda_shift', cls.INITIAL, cls.BACK))
        else:
            start_idx = 3
            transitions.append(Transition('lambda_shift', cls.FINISH,
                                          cls.BACK))
            # initial -> first question
            transitions.append(
                Transition('lambda_shift', cls.INITIAL,
                           states[start_idx].name))
            # last question -> finish
            transitions.append(
                Transition('move',
                           states[-1].name,
                           cls.FINISH,
                           conditions="is_answer_valid"))
            for i in range(start_idx, length - 1):
                transitions.append(
                    Transition('move',
                               states[i].name,
                               states[i + 1].name,
                               conditions="is_answer_valid"))
        return transitions

    def toNestedState(self, remap: str) -> DotMap:
        return DotMap({
            'name': self.name,
            'children': self,
            'remap': {
                self.BACK: remap
            }
        })


class ConversationFunction:
    # hostname = 'https://panda-transport.herokuapp.com/'
    hostname = 'https://e9402c21.ngrok.io'

    @classmethod
    def show_fsm(cls, model):
        model.get_graph().draw(f"img/fsm_{model.user.user_id}.png",
                               prog="dot",
                               format="png")
        image_url = f"{cls.hostname}/show-client-fsm?img=fsm_{model.user.user_id}"
        print(image_url)
        return MsgBuilder.image(image_url, image_url)

    @classmethod
    def query_train_info_by_time(cls, model):
        answer = model.get_answer()
        start_station = answer[0]
        end_station = answer[1]
        result = THSR.query_train_info_by_time(start_station, end_station)
        print(result)
        carousel_columns = list()
        if len(result) == 0:
            return MsgBuilder.text("今天無其他車次")
        for r in result:
            carousel_columns.append(cls.make_train_info_column(r))
        return MsgBuilder.carousel(carousel_columns)

    @classmethod
    def make_train_info_column(cls, r):
        title = f"{r['OriginStopTime']['DepartureTime']}->{r['DestinationStopTime']['ArrivalTime']}"
        text = f"{r['OriginStopTime']['StationName']['Zh_tw']}->{r['DestinationStopTime']['StationName']['Zh_tw']}"
        train_no = f"No.{r['DailyTrainInfo']['TrainNo']}"
        action = ActionBuilder.msg("其他服務", "其他服務")
        return ActionBuilder.carousel_column(text=f"{text}\n{train_no}",
                                             title=title,actions=[action])


def conversation():
    return Conversation([
        Qs.ASK_START_STATION,
        Qs.ASK_END_STATION,
        Qs.ASK_NORTH_OR_SOUTH,
    ],
                        None,
                        text=u"查詢車站起訖車次")


class AppConversations:
    QUERY_NOW_TRAIN_INFO = \
        Conversation([
            Qs.ASK_START_STATION,
            Qs.ASK_END_STATION,
        ],finish_msg=ConversationFunction.query_train_info_by_time,
                     text=u"查詢現在起訖站車次",
                     name="show_train_info_from_now",
                     trigger="train_info_from_now")
    SHOW_FSM = Conversation([],
                            finish_msg=ConversationFunction.show_fsm,
                            name="show_fsm",
                            text=u"查看fsm",
                            trigger="show_fsm")