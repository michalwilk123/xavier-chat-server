from fastapi import APIRouter, WebSocket
from fastapi.param_functions import Depends
from fastapi.security import HTTPBasicCredentials
from app.chat.connection import (
    close_websocket_con,
    send_chat_message_via_websockets,
    check_if_user_available,
    add_new_websocket_con,
)
from app.db.chat import send_chat_message_to_absent_user
from fastapi.websockets import WebSocketDisconnect
from app.models.websocket_init import WebsocketInit
from app.db.user import user_auth
from app.db import chat
from .deps import http_basic_security

chat_router = APIRouter(prefix="/chat")


async def send_chat_message(websock: WebSocket, login: str):
    # if check_if_user_available(login):
    #     await send_chat_message_via_websockets(login, msg)
    # else:
    # await send_chat_message_to_absent_user(login, msg)
    ...


@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, data: WebsocketInit):
    await websocket.accept()
    await add_new_websocket_con(data.my_login, data.signature, websocket)

    try:
        await send_chat_message(websocket, data.contact_login)
    except WebSocketDisconnect:
        await close_websocket_con(data.my_login, data.signature)


@chat_router.get("")
async def get_pending_messages(
    credentials: HTTPBasicCredentials = Depends(http_basic_security),
):
    ...
    # if not await user_auth(credentials.username, credentials.password):
    #     return {"response": "not authorized"}

    # messages = await chat.get_pending_messages(credentials.username)
    # return {"pending_messages": messages}
