from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import DefaultSettings
from src.core.containers import Container
from src.endpoints.api import routers
from src.endpoints.middlewares import middlewares


def bind_routers(app: FastAPI) -> None:
    for router in routers:
        app.include_router(
            router=router,
        )


def bind_middlewares(app: FastAPI) -> None:
    for middleware in middlewares:
        middle = middleware()
        app.add_middleware(
            middleware_class=BaseHTTPMiddleware,
            dispatch=middle
        )


def get_application(settings: DefaultSettings = None) -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=settings.OPENAPI_URL,
        docs_url=settings.DOCS_URL,
    )
    container = Container()
    container.config.from_dict(settings.model_dump())
    bind_routers(app)
    # bind_middlewares(app)
    return app


__all__ = [
    'get_application'
]
