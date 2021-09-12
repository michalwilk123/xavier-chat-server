from fastapi import APIRouter, Depends
from fastapi.concurrency import run_until_first_complete
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.websockets import WebSocket

from app.chat import connection
from app.db.chat import get_conversation_address
from app.models.crypto import FakeJWT

from .deps import authenticate_user, get_db

# cannot set prefix in the router due to fastapi bug
chat_router = APIRouter()


@chat_router.websocket("/chat/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    login: str,
    participant: str,
    db: Session = Depends(get_db),
):
    await websocket.accept()
    msg = await websocket.receive_json()
    signature = FakeJWT(**msg)

    authenticate_user(signature, login, db)

    # check if particip exists
    address = get_conversation_address(db, login, participant)

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Naura"
        )

    await run_until_first_complete(
        (
            connection.chatroom_ws_receiver,
            {"websocket": websocket, "channel": address},
        ),
        (
            connection.chatroom_ws_sender,
            {"websocket": websocket, "channel": address},
        ),
    )
