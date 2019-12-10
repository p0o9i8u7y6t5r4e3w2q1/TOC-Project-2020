# -*- coding: utf-8 -*-

import os
from typing import List
from pymongo import MongoClient
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json  # type: ignore
from dotenv import load_dotenv


@dataclass_json
@dataclass
class Status:
    state: str = ''
    answers: List[str] = field(default_factory=list)

    def reset(self, state: str):
        self.state = state
        self.answers = list()


@dataclass_json
@dataclass
class User:
    user_id: str
    status: Status = Status()

    def reset_status(self, state: str):
        self.status.reset(state)

    def set_state(self, state: str):
        self.status.state = state

    def add_answer(self, answer):
        self.status.answers.append(answer)


class Database:
    database_name = "transport_panda"
    collection_name = "user"
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = Database()
        return cls.instance

    def __init__(self):
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URL", None))
        self.client.server_info()  # 判断是否连接成功
        self.user_collection = self.client[self.database_name][
            self.collection_name]

    def find(self, user_id: str) -> User:
        user = self.user_collection.find_one({'user_id': user_id})
        if user is not None:
            # pylint: disable=E1101
            user = User.from_dict(user)  # type: ignore
            print(user)
        return user

    def save(self, user: User):
        self.user_collection \
            .replace_one({'user_id': user.user_id},
                         user.to_dict(),  # type: ignore
                         upsert=True)
