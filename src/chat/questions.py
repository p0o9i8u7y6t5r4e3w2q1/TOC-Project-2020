# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any, Optional

from linebot.models import Event, SendMessage
from returns.maybe import Maybe, maybe

from api.transport_api import THSR
from transitions.extensions.nesting import NestedState
from utils.bot_msg import ActionBuilder, MsgBuilder


class Question(metaclass=ABCMeta):
    def __init__(self,
                 question_msg: SendMessage,
                 error_msg: SendMessage,
                 name: str = 'question'):
        self.name = name
        self.question_msg: SendMessage = question_msg
        self.error_msg: SendMessage = error_msg

    # if answer is valid return mapped value
    @abstractmethod
    def check_answer(self, answer: Any) -> Any:
        return NotImplemented


class AskStationQuestion(Question):
    def __init__(self, question: str, name: str = 'ask_station_question'):
        # TODO error_msg
        super().__init__(MsgBuilder.text(question), MsgBuilder.text("查無此車站"),
                         name)

    def check_answer(self, answer: Event) -> Optional[str]:
        print(answer.message.text)
        try:
            return THSR.station_info(answer.message.text)['StationID']
        except:
            return None


class ConfirmQuestion(Question):
    def __init__(self,
                 question: str,
                 left_text: str,
                 right_text: str,
                 name: str = 'confirm_question'):
        self.left_text = left_text
        self.right_text = right_text
        question_msg = MsgBuilder.confirm(question,
                                          ActionBuilder.msg(left_text),
                                          ActionBuilder.msg(right_text))
        super().__init__(question_msg, MsgBuilder.text("輸入錯誤，請重新輸入"),
                         name)  # TODO error_msg

    @maybe
    def check_answer(self, answer: str) -> Optional[str]:
        if answer not in (self.left_text, self.right_text):
            return None
        return answer


class QuestionBuilder:
    ASK_START_STATION = \
        AskStationQuestion("在哪一站搭車?(例如：台北)", name='ask_start_station')

    ASK_END_STATION = \
        AskStationQuestion("在哪一站下車?(例如：左營)", name='ask_end_station')

    ASK_NORTH_OR_SOUTH = \
        ConfirmQuestion("往北上或南下?", "北上", "南下", name='ask_north_or_south')
