from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import get_config
from src.core.containers import Container
from src.endpoints.api import v1_routers
from src.endpoints.middlewares import middlewares


config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Container()
    yield


def bind_routers(app: FastAPI) -> None:
    for router in v1_routers:
        app.include_router(
            router=router,
            prefix='/v1'
        )


def bind_middleware(app: FastAPI) -> None:
    for middleware in middlewares:
        app.add_middleware(
            middleware_class=BaseHTTPMiddleware,
            dispatch=middleware
        )


def get_application() -> FastAPI:
    app = FastAPI(
        title=config.PROJECT_NAME,
        openapi_url=config.OPENAPI_URL,
        docs_url=config.DOCS_URL,
        lifespan=lifespan
    )

    bind_routers(app)
    bind_middleware(app)
    return app


__all__ = [
    'get_application'
]
