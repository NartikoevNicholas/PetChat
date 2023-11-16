import typing as tp

from fastapi.responses import JSONResponse
from fastapi import (
    APIRouter,
    status,
    Depends
)
from dependency_injector.wiring import inject

from src.endpoints.middlewares import AuthMiddleware
from src.endpoints.dependencies import auth_depends
from src.services import entities as et

from . import api


router = APIRouter(
    prefix=f'/{api.ROUTER_AUTH}',
    tags=['auth']
)


@router.post(
    path=f'/{api.AUTH_LOGIN}',
    response_model=et.JWTToken
)
@inject
async def login(
    data: tp.Union[et.UserCredUsername, et.UserCredEmail],
    auth_service=auth_depends
):
    return await auth_service.authenticate(data)


@router.post(
    path=f'/{api.AUTH_REFRESH}',
    response_model=et.JWTToken
)
@inject
async def refresh_token(
    jwt_refresh_token: et.JWTRefreshToken,
    auth_service=auth_depends
):
    return await auth_service.refresh_token(jwt_refresh_token)


@router.post(
    path=f'/{api.AUTH_LOGOUT}'
)
@inject
async def logout(
    jwt_token: et.JWTToken,
    jwt_payload: et.JWTPayload = Depends(AuthMiddleware.verify_access_token),
    auth_service=auth_depends
):
    await auth_service.logout(jwt_payload.user_id, jwt_token)
    return JSONResponse(
        content={'msg': 'successful logout'},
        status_code=status.HTTP_200_OK
    )
