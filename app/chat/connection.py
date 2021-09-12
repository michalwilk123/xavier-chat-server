from app.config import get_settings
from broadcaster import Broadcast
import asyncio_redis

broadcast = Broadcast(get_settings().broadcaster_source)


async def chatroom_ws_receiver(websocket, channel: str):
    await broadcast.publish(channel=channel, message="PING")

    async for message in websocket.iter_text():
        await broadcast.publish(channel=channel, message=message)


async def chatroom_ws_sender(websocket, channel: str):
    async with broadcast.subscribe(channel=channel) as subscriber:
        async for event in subscriber:
            if event.message == "PING":
                await websocket.send_text("PONG")

            await websocket.send_text(event.message)
