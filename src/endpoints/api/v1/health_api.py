from fastapi import APIRouter


router = APIRouter(
    prefix='/v1/health'
)


@router.get(
    path='/pong'
)
async def ping():
    print('1')
    return {'msg': 'pong'}
