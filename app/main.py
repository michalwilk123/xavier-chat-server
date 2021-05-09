from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from .routers import user_router, chat_router, contact_router
from app.config import AppInformation

app = FastAPI()
app_information = AppInformation()


@app.get("/")
@app.get("/about")
async def root():
    return {"about": "hello to my simple chat rest api"}

@app.get('/alive')
async def is_alive():
    return {'alive' : True}


app.include_router(user_router)
app.include_router(chat_router)
app.include_router(contact_router)


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
