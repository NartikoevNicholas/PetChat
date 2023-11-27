from uuid import UUID
from typing import Union

from fastapi import (
    APIRouter,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject

from src.core.config import API
from src.services.use_case import UserService
from src.endpoints.dependencies import (
    AuthUser,
    user_depends
)
from src.services.entities import (
    UserResponseDTO,
    UserRequestDTO,
    UserUsernameDTO,
    UserEmailDTO,
    UserPasswordDTO,
    UserEmailPasswordDTO,
    UserUsernamePasswordDTO,
    UserUpdateType
)


router = APIRouter(
    tags=['user']
)


@router.post(path=API.user_registration_v1)
@inject
async def user_registration(request: Request,
                            data: UserRequestDTO,
                            user_service: UserService = user_depends):
    await user_service.registration(request, data)
    return JSONResponse(
        content={'msg': 'successful'},
        status_code=status.HTTP_201_CREATED
    )


@router.get(path=f'{API.user_email_verify_v1}/{{user_id}}/{{user_code}}')
@inject
async def user_verification(user_id: UUID,
                            user_code: str,
                            user_service: UserService = user_depends):

    await user_service.email_verify(user_id, user_code)
    return JSONResponse(
        content={'msg': 'user successful created'},
        status_code=status.HTTP_200_OK
    )


@router.post(path=API.user_available_v1)
@inject
async def available(data: Union[UserUsernameDTO, UserEmailDTO],
                    user_service: UserService = user_depends):
    await user_service.available(data)
    return JSONResponse(
        content={'msg': 'username available'},
        status_code=status.HTTP_200_OK
    )


@router.get(path=API.user_me_v1,
            response_model=UserResponseDTO)
@inject
async def user_me(auth_user: AuthUser,
                  user_service: UserService = user_depends):
    token, payload = auth_user
    return await user_service.me(payload.user_id)


@router.patch(path=API.user_update_v1,
              response_model=UserResponseDTO)
@inject
async def user_update(request: Request,
                      data: UserUpdateType,
                      auth_user: AuthUser,
                      user_service=user_depends):
    token, payload = auth_user
    if isinstance(data, UserUsernamePasswordDTO):
        user_data = await user_service.update_username(payload.user_id, data)

    elif isinstance(data, UserEmailPasswordDTO):
        user_data = await user_service.update_email(request, payload.user_id, data)

    else:
        user_data = await user_service.update_password(payload.user_id, data)

    return user_data


@router.delete(path=API.user_delete_v1)
@inject
async def user_delete(data: UserPasswordDTO,
                      auth_user: AuthUser,
                      user_service=user_depends):
    token, payload = auth_user
    await user_service.remove(payload, token, data)
    return JSONResponse(
        content={'msg': 'No content!'},
        status_code=status.HTTP_204_NO_CONTENT
    )
