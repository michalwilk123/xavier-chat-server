from enum import Enum, auto


class ChatServerRequest(Enum):
    INVITE_TO_CONVERSATION = auto()
    CHECK_FOR_CONVERSATIONS = auto()
    DISCONNECT = auto()
    INVITE = auto()
    INVITE = auto()


def message_dispatcher():
    ...
