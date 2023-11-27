import uuid
from typing import (
    Union,
    Optional
)

from httpx import (
    AsyncClient,
    Response
)
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import (
    API,
    DefaultSettings
)
from src.services.entities import (
    JWTToken,
    JWTRefreshToken,
    UserPasswordDTO,
    UserEmailPasswordDTO,
    UserUsernamePasswordDTO,
    UserUsernameDTO,
    UserEmailDTO,
    UserUpdateType
)
from src.infrastructure.repository.postgres_models import User


class UserSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_superuser: Optional[bool] = None


def get_user(username: Optional[str] = 'testtest',
             email: Optional[str] = 'test@email.ru',
             password: Optional[str] = 'testtest',
             is_superuser: Optional[bool] = False) -> UserSchema:
    return UserSchema(
        username=username,
        email=email,
        password=password,
        is_superuser=is_superuser
    )


async def get_code(redis: Redis,
                   settings: DefaultSettings,
                   user_id: uuid.UUID) -> str:
    code = await redis.get(user_id.hex)
    code = code.decode().split(settings.SEP)[-1]
    return code


async def get_user_id(session: AsyncSession,
                      username: str) -> Optional[uuid.UUID]:

    obj = await session.execute(
        select(User.id)
        .where(User.username.__eq__(username))
    )
    return obj.scalar()


async def verify_email_handler(client: AsyncClient,
                               user_id: Optional[uuid.UUID],
                               code: Optional[str]) -> Response:
    data = [API.user_email_verify_v1]
    if user_id is not None:
        data.append(user_id.hex)

    if code is not None:
        data.append(code)

    return await client.get(url='/'.join(data))


async def registration_handler(client: AsyncClient,
                               content: Optional[UserSchema]) -> Response:
    data = {'url': API.user_registration_v1}
    if content:
        data['content'] = content.model_dump_json(exclude_none=True)

    return await client.post(**data)


async def update_user_handler(client: AsyncClient,
                              content: Optional[UserUpdateType],
                              header_token: Optional[str]) -> Response:
    data = {'url': API.user_update_v1}
    if content is not None:
        data['content'] = content.model_dump_json()

    if header_token is not None:
        data['headers'] = {'Authorization': f'Bearer {header_token}'}

    return await client.patch(**data)


async def delete_user_handler(client: AsyncClient,
                              content: Optional[UserPasswordDTO],
                              header_token: Optional[str]) -> Response:
    data = {
        'method': 'DELETE',
        'url': API.user_delete_v1
    }
    if content is not None:
        data['content'] = content.model_dump_json(exclude_none=True)

    if header_token is not None:
        data['headers'] = {'Authorization': f'Bearer {header_token}'}

    return await client.request(**data)


async def auth_handler(client: AsyncClient,
                       content: Union[UserEmailPasswordDTO, UserUsernamePasswordDTO]) -> Response:
    data = {'url': API.auth_login_v1}
    if content:
        data['content'] = content.model_dump_json(exclude_none=True)

    return await client.post(**data)


async def logout_handler(client: AsyncClient,
                         content: Optional[JWTToken],
                         header_token: Optional[str]) -> Response:
    data = {'url': API.auth_logout_v1}
    if content:
        data['content'] = content.model_dump_json(exclude_none=True)

    if header_token:
        data['headers'] = {'Authorization': f'Bearer {header_token}'}

    return await client.post(**data)


async def refresh_handler(client: AsyncClient,
                          content: Optional[JWTRefreshToken]) -> Response:
    data = {'url': API.auth_refresh_v1}
    if content is not None:
        data['content'] = content.model_dump_json(exclude_none=True)
    return await client.post(**data)


async def available_handler(client: AsyncClient,
                            content: Union[UserUsernameDTO, UserEmailDTO] = None) -> Response:
    data = {'url': API.user_available_v1}
    if content is not None:
        data['content'] = content.model_dump_json(exclude_none=True)

    return await client.post(**data)


async def me_handler(client: AsyncClient,
                     header_token: Optional[str]) -> Response:
    data = {'url': API.user_me_v1}
    if header_token is not None:
        data['headers'] = {'Authorization': f'Bearer {header_token}'}
    return await client.get(**data)
