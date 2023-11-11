from fastapi import APIRouter


router = APIRouter(
    prefix='/v1/health'
)


@router.get(
    path='/pong'
)
async def ping():
    return {'msg': 'pong'}
