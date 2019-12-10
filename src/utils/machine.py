from typing import List
from transitions.extensions.nesting import NestedState

from dotmap import DotMap
from linebot.models import SendMessage

class ObjectState(NestedState):
    def __init__(self, obj, **kwargs):
        super().__init__(**kwargs)
        self.obj = obj


class MessageState(NestedState):
    def __init__(self, msg, **kwargs):
        super().__init__(**kwargs)
        if callable(msg):
            self.message = msg
        else:
            self.msg = msg
            self.message = lambda param: msg


def Transition(trigger,
               source,
               dest,
               before=None,
               after=None,
               conditions=None,
               unless=None) -> DotMap:
    return DotMap({
        'trigger': trigger,
        'source': source,
        'dest': dest,
        'before': before,
        'after': after,
        'conditions': conditions,
        'unless': unless
    })


# NOT USE
# make sequence style transitions
def sequence(states: List, trigger: str) -> List[DotMap]:
    # each state: { name: str}
    length = len(states)
    transitions = list()
    for i in range(length - 1):
        transitions.append(
            Transition(trigger,
                       states[i].name,
                       states[i + 1].name,
                       conditions="can_move"))
    return transitions


# NOT USE
# make tree style transitions
def tree(root_state, child_states: List) -> List[DotMap]:
    # each state: { name: str, trigger: str }
    transitions = list()
    for i, s in enumerate(child_states):
        transitions.append(Transition(s.trigger, root_state, s.name))
    return transitions
