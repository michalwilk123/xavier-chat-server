from fastapi import APIRouter, WebSocket, Body
from app.chat.connection import (
    close_websocket_con,
    send_chat_message_via_websockets,
    check_if_user_available,
    add_new_websocket_con,
)
from app.db.chat import send_chat_message_to_absent_user
from fastapi.websockets import WebSocketDisconnect
from app.models.websocket_init import WebsocketInit
from app.models.user_model import BasicUserAuthorization
from app.db.user import user_auth
from app.db import chat

chat_router = APIRouter(prefix="/chat")


async def send_chat_message(websock: WebSocket, login: str):
    async for msg in websock:
        if check_if_user_available(login):
            await send_chat_message_via_websockets(login, msg)
        else:
            await send_chat_message_to_absent_user(login, msg)


@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, data: WebsocketInit):
    await websocket.accept()
    await add_new_websocket_con(data.my_login, data.signature, websocket)

    try:
        await send_chat_message(websocket, data.contact_login)
    except WebSocketDisconnect:
        await close_websocket_con(data.my_login, data.signature)


@chat_router.get("")
async def get_pending_messages(credentials: BasicUserAuthorization):
    if not await user_auth(credentials.login, credentials.signature):
        return {"response": "not authorized"}

    messages = await chat.get_pending_messages(credentials.login)
    return {"pending_messages": messages}
