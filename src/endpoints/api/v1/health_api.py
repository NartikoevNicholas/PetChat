from fastapi import APIRouter

from . import api


router = APIRouter(
    prefix=f'/{api.ROUTER_HEALTH}',
    tags=['health']
)


@router.get(
    path=api.HEALTH_PING
)
async def ping():
    return {'msg': 'pong'}
