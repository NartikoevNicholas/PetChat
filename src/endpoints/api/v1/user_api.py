from uuid import UUID

from fastapi import (
    APIRouter,
    Request,
)
from fastapi import status
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject

from src.endpoints.dependencies import user_depends
from src.services import entities as et

from . import api


router = APIRouter(
    prefix=f'/{api.ROUTER_USER}',
    tags=['user']
)


@router.post(
    path=f'/{api.USER_REGISTRATION}'
)
@inject
async def user_registration(
    request: Request,
    data: et.UserDTO,
    user_service=user_depends,
):
    await user_service.registration(request, data)
    return JSONResponse(
        content={'msg': 'successful'},
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    path=f'/{api.USER_REGISTRATION_VERIFY}/{{user_id}}/{{user_code}}'
)
@inject
async def user_verification(
    user_id: UUID,
    user_code: str,
    user_service=user_depends,
):
    if await user_service.email_verify(user_id, user_code):
        return JSONResponse(
            content={'msg': 'user successful created'},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={'msg': 'user is not exist'},
        status_code=status.HTTP_404_NOT_FOUND
    )


@router.post(
    path=f'/{api.USER_AVAILABLE_USERNAME}'
)
@inject
async def available_username(
    data: et.UserUsername,
    user_service=user_depends,
):
    if await user_service.available_username(data):
        return JSONResponse(
            content={'msg': 'username available'},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={'msg': 'username unavailable'},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@router.post(
    path=f'/{api.USER_AVAILABLE_EMAIL}'
)
@inject
async def available_email(
    data: et.UserEmail,
    user_service=user_depends
):
    if await user_service.available_email(data):
        return JSONResponse(
            content={'msg': 'username available'},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={'msg': 'username unavailable'},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
