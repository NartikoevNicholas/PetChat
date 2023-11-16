from .v1 import (
    user_api,
    health_api,
    auth_api,
)


v1_routers = [
    user_api.router,
    health_api.router,
    auth_api.router
]


__all__ = [
    'v1_routers'
]
