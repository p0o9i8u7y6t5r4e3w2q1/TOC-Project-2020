# -*- coding: utf-8 -*-

from typing import Optional, List
from linebot.models import (TextSendMessage, TemplateSendMessage,CarouselTemplate,
                            ImageSendMessage, ConfirmTemplate, MessageAction,
                            CarouselColumn, Action, PostbackAction, URIAction,
                            ButtonsTemplate)
from returns.maybe import Maybe


class MsgBuilder:
    @staticmethod
    def text(text: str) -> TextSendMessage:
        return TextSendMessage(text)

    @staticmethod
    def image(origin_url: str, preview_url: str) -> ImageSendMessage:
        return ImageSendMessage(origin_url, preview_url)

    @staticmethod
    def confirm(text: str, left_action: Action,
                right_action: Action) -> TemplateSendMessage:
        return TemplateSendMessage(alt_text="您有新訊息",
                                   template=ConfirmTemplate(
                                       text,
                                       actions=[left_action, right_action]))

    @staticmethod
    def buttons(text: str, actions: List[Action],
                title=None) -> TemplateSendMessage:
        return TemplateSendMessage(title=None,
                                   alt_text="您有新訊息",
                                   template=ButtonsTemplate(text,
                                                            actions=actions))

    @staticmethod
    def carousel(columns: List) -> TemplateSendMessage:
        return TemplateSendMessage(title=None,
                                   alt_text="您有新訊息",
                                   template=CarouselTemplate(columns=columns))


class ActionBuilder:
    @staticmethod
    def msg(label: str, text: Optional[str] = None) -> MessageAction:
        return MessageAction(label, Maybe.new(text).value_or(label))

    @staticmethod
    def postback(label: str, data, display_text: str) -> PostbackAction:
        return PostbackAction(label, data, display_text)

    @staticmethod
    def uri(label, uri, alt_uri) -> URIAction:
        return URIAction(label, uri, alt_uri)

    @staticmethod
    def carousel_column(text: str, title=None, image_url=None, actions=None):
        return CarouselColumn(text=text,
                              title=title,
                              thumbnail_image_url=image_url,
                              actions=actions)
