from pydantic import BaseModel


class WebsocketInit(BaseModel):
    my_login: str
    contact_login: str
    signature: str
