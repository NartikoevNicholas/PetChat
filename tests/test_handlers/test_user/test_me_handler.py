import asyncio
import json

from src.endpoints.exceptions import (
    TokenTypeInvalidHTTPException
)
from src.services.entities import (
    JWTToken,
    JWTRefreshToken,
    UserPasswordDTO,
    UserResponseDTO,
    UserUsernamePasswordDTO
)

from tests.test_handlers.utils import (
    get_user,
    get_user_id,
    get_code,
    me_handler,
    auth_handler,
    refresh_handler,
    delete_user_handler,
    registration_handler,
    verify_email_handler,
)


class TestMeHandler:
    async def test_1(self, client, session, redis, settings):
        """
        1. Create user               response 201
        2. Verify user email         response 200
        3. Auth user                 response 200
        4. Get me with access token  response 200
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify user email
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Get me
        token = JWTToken.model_validate_json(response.text)
        response = await me_handler(client, token.access_token)
        assert response.status_code == 200
        assert UserResponseDTO.model_validate_json(response.text).username == user.username

    async def test_2(self, client, session, redis, settings):
        """
        1. Create user                 response 201
        2. Verify user email           response 200
        3. Auth user                   response 200
        4. Get me with refresh token   response 400
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify user email
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Get me
        token = JWTToken.model_validate_json(response.text)
        response = await me_handler(client, token.refresh_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenTypeInvalidHTTPException().detail

    async def test_3(self, client, session, redis, settings):
        """
        1. Create user
        2. Verify email user
        3. Auth user
        4. Get me
        5. Sleep ACCESS_EXP_TIME
        6. Get me
        7. Refresh token
        8. Get me
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify user email
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Get me
        token = JWTToken.model_validate_json(response.text)
        response = await me_handler(client, token.access_token)
        assert response.status_code == 200
        assert UserResponseDTO.model_validate_json(response.text).username == user.username

        # 5. Sleep ACCESS_EXP_TIME and 6. Get me
        await asyncio.sleep(settings.ACCESS_EXP_TIME)
        response = await me_handler(client, token.access_token)
        assert response.status_code == 400

        # 7. Refresh handler
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200

        # 8. Get me
        token = JWTToken.model_validate_json(response.text)
        response = await me_handler(client, token.access_token)
        assert response.status_code == 200

    async def test_4(self, client, session, redis, settings):
        """
        1. Create user        response 201
        2. Verify user email  response 200
        3. Auth user          response 200
        4. Get me             response 200
        5. Delete user        response 204
        6. Get me             response 400
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify user email
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Get me
        token = JWTToken.model_validate_json(response.text)
        response = await me_handler(client, token.access_token)
        assert response.status_code == 200
        assert UserResponseDTO.model_validate_json(response.text).username == user.username

        # 5. Delete user
        user_password = UserPasswordDTO(password=user.password)
        response = await delete_user_handler(client, user_password, token.access_token)
        assert response.status_code == 204

        # 6. Get me
        response = await me_handler(client, token.access_token)
        assert response.status_code == 400
