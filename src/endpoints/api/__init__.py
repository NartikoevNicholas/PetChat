from .v1 import (
    user_api,
    health_api
)


routers = [
    user_api.router,
    health_api.router
]


__all__ = [
    'routers'
]
