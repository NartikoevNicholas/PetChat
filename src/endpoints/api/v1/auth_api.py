
from fastapi.responses import JSONResponse
from fastapi import (
    APIRouter,
    status
)
from dependency_injector.wiring import inject

from src.core.config import API
from src.endpoints.dependencies import (
    auth_depends,
    AuthUser
)
from src.services.entities import (
    JWTToken,
    LoginType,
    JWTRefreshToken
)


router = APIRouter(tags=['auth'])


@router.post(path=API.auth_login_v1,
             response_model=JWTToken)
@inject
async def login(data: LoginType,
                auth_service=auth_depends):
    return await auth_service.authenticate(data)


@router.post(path=API.auth_refresh_v1,
             response_model=JWTToken)
@inject
async def refresh_token(jwt_refresh_token: JWTRefreshToken,
                        auth_service=auth_depends):
    return await auth_service.refresh_token(jwt_refresh_token)


@router.post(path=API.auth_logout_v1)
@inject
async def logout(jwt_token: JWTToken,
                 auth_user: AuthUser,
                 auth_service=auth_depends):
    token, user = auth_user
    await auth_service.logout(user.user_id, jwt_token)
    return JSONResponse(
        content={'msg': 'successful logout'},
        status_code=status.HTTP_200_OK
    )
