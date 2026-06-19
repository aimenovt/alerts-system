from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.messaging.connection import rabbitmq_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    await rabbitmq_manager.connect()
    try:
        yield
    finally:
        await rabbitmq_manager.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
