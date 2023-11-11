from uuid import UUID

from fastapi import (
    APIRouter,
    Request,
    Depends
)
from fastapi import status
from fastapi.responses import JSONResponse

from dependency_injector.wiring import inject, Provide

from src.core.containers import Container
from src.services.use_case import UserUseCase
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
    user_use_case: UserUseCase = Depends(Provide[Container.user_use_case]),
):
    await user_use_case.registration(request, data)
    return JSONResponse(
        content={'msg': 'successful'},
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    path='/registrasion/verify/{user_id}/{user_code}'
)
@inject
async def user_verification(
    request: Request,
    user_id: UUID,
    user_code: str,
    user_use_case: UserUseCase = Depends(Provide[Container.user_use_case])
):
    if await user_use_case.email_verify(user_id, user_code):
        return JSONResponse(
            content={'msg': 'user successful created'},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={'msg': 'user is not exist'},
        status_code=status.HTTP_404_NOT_FOUND
    )
