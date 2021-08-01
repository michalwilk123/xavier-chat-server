from typing import Dict
from fastapi import WebSocket

dict_of_websocket_connections: Dict[str, WebSocket] = {}


class ChatUserException(Exception):
    ...


def check_if_user_available(login: str) -> bool:
    return login in dict_of_websocket_connections


async def send_chat_message_via_websockets(login: str, data: str):
    try:
        ws: WebSocket = dict_of_websocket_connections[login]
    except KeyError:
        raise ChatUserException("There is no active user with given login")

    await ws.send_text(data)


async def add_new_websocket_con(
    my_login: str, signature: str, websock: WebSocket
):
    # if await user_auth(my_login, signature):
    #     dict_of_websocket_connections[my_login] = websock
    ...


async def close_websocket_con(login: str, signature: str):
    # if await user_auth(login, signature):
    #     dict_of_websocket_connections.pop(login)
    ...
