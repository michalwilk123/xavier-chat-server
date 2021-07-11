from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.routers.user import user_router
from app.routers.chat import chat_router
from app.routers.crypto import crypto_router
from app.routers.contacts import contact_router
from app.config import AppInformation

app = FastAPI()
app_information = AppInformation()


@app.get("/")
@app.get("/about")
async def root():
    return {"about": "hello to my simple chat rest api"}


@app.get("/alive")
async def is_alive():
    return "OK"


# this MUST be BEFORE app include commands!
user_router.include_router(crypto_router)
user_router.include_router(contact_router)

app.include_router(user_router)
app.include_router(chat_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    print(dir(AppInformation))

    openapi_schema = get_openapi(
        title=app_information.APP_NAME,
        version=app_information.VERSION,
        description=app_information.DESCRIPTION,
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
