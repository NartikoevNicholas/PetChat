from uuid import UUID

from fastapi import (
    APIRouter,
    Request,
)
from fastapi import status
from fastapi.responses import JSONResponse

from pydantic import EmailStr

from dependency_injector.wiring import inject

from src.endpoints.dependencies import user_depends
from src.services.entities import UserCreateEntity


router = APIRouter(
    prefix='/v1/user'
)


@router.post(
    path='/registrasion'
)
@inject
async def user_registration(
    request: Request,
    data: UserCreateEntity,
    user_service=user_depends,
):
    await user_service.registration(request, data)
    return JSONResponse(
        content={'msg': 'successful'},
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    path='/registrasion/verify/{user_id}/{user_code}'
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


@router.get(
    path='/available/username={username}'
)
@inject
async def available_username(
    username: str,
    user_service=user_depends,
):
    if await user_service.available_username(username):
        return JSONResponse(
            content={'msg': 'username available'},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={'msg': 'username unavailable'},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@router.get(
    path='/available/email={email}'
)
@inject
async def available_email(
    email: EmailStr,
    user_service=user_depends
):
    if await user_service.available_email(email):
        return JSONResponse(
            content={'msg': 'username available'},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={'msg': 'username unavailable'},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
