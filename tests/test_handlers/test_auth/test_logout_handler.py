import asyncio
import json

from src.endpoints.exceptions import (
    TokenInvalidHTTPException,
    TokenExpiredHTTPException
)
from src.services.entities import (
    JWTToken,
    JWTRefreshToken,
    UserPasswordDTO,
    UserUsernamePasswordDTO
)

from tests.test_handlers.utils import (
    get_user,
    get_code,
    get_user_id,
    auth_handler,
    logout_handler,
    refresh_handler,
    delete_user_handler,
    registration_handler,
    verify_email_handler,
)


class TestLogoutHandler:
    async def test_1(self, client, session, redis, settings):
        """
        1. Create user          response 201
        2. Verify user email    response 200
        3. Auth user            response 200
        4. logout user          response 200
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

        # 4. logout user
        token = JWTToken.model_validate_json(response.text)
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 200

    async def test_2(self, client, session, redis, settings):
        """
        1. Create user          response 201
        2. Verify user email    response 200
        3. Auth user            response 200
        4. Logout user          response 200
        5. Repeat logout        response 400
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

        # 4. Logout user
        token = JWTToken.model_validate_json(response.text)
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 200

        # 5. Repeat logout
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenInvalidHTTPException().detail

    async def test_3(self, client, session, redis, settings):
        """
        1. Create user            response 201
        2. Verify user email      response 200
        3. Auth user              response 200
        4. Sleep ACCESS_EXP_TIME
        5. Logout user            response 400
        6. Refresh token          response 200
        7. Logout user            response 200
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

        # 4. Sleep ACCESS_EXP_TIME and 5. Logout user
        await asyncio.sleep(settings.ACCESS_EXP_TIME)
        token = JWTToken.model_validate_json(response.text)
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenExpiredHTTPException().detail

        # 6. Refresh token
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200

        # 7. Logout user
        token = JWTToken.model_validate_json(response.text)
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 200

    async def test_4(self, client, session, redis, settings):
        """
        1. Create user                         response 201
        2. Verify user email                   response 200
        3. Auth user                           response 200
        4. Logout user                         response 200
        5. Auth user                           response 200
        6. Delete user with old access-token   response 400
        7. Delete user with new access-token   response 204
        8. Logout user                         response 400
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

        # 4. Logout user
        token = JWTToken.model_validate_json(response.text)
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 200

        # 5. Auth user
        response = await auth_handler(client, login)
        assert response.status_code == 200
        new_token = JWTToken.model_validate_json(response.text)

        # 6. Delete user with old access-token
        user_password = UserPasswordDTO(password=user.password)
        response = await delete_user_handler(client, user_password, token.access_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenInvalidHTTPException().detail

        # 7. Delete user with new access-token
        response = await delete_user_handler(client, user_password, new_token.access_token)
        assert response.status_code == 204

        # 8. Logout user
        response = await logout_handler(client, new_token, new_token.access_token)
        assert response.status_code == 400
