import asyncio
import json

from src.endpoints.exceptions import (
    TokenInvalidHTTPException,
    TokenExpiredHTTPException,
    TokenDeletedHTTPException,
    TokenTypeInvalidHTTPException
)
from src.services.entities import (
    JWTToken,
    UserEmailPasswordDTO,
    JWTRefreshToken,
    UserPasswordDTO,
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


class TestRefreshHandler:
    async def test_1(self, client, session, redis, settings):
        """
        1. Create user             response 201
        2. Verify email            response 200
        3. Auth user               response 200
        4. Refresh refresh-token   response 200
        """
        # 1
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200

    async def test_2(self, client, session, redis, settings):
        """
        1. Create user           response 201
        2. Verify email          response 200
        3. Auth user             response 200
        4. Refresh access-token  response 400
        """
        # 1
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.access_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenTypeInvalidHTTPException().detail

    async def test_3(self, client, session, redis, settings):
        """
        1. Create user,        response 201
        2. Verify email user,  response 200
        3. Auth user,          response 200
        4. Refresh token,      response 200
        5. Delete user,        response 204
        6. Refresh token       response 400
        """
        # 1
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200
        new_token = JWTToken.model_validate_json(response.text)

        # 5
        user_password = UserPasswordDTO(password=user.password)
        response = await delete_user_handler(client, user_password, token.access_token)
        assert response.status_code == 204

        # 6
        refresh_token = JWTRefreshToken(refresh_token=new_token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenDeletedHTTPException().detail

    async def test_4(self, client, session, redis, settings):
        """
        1. Create user            response 201
        2. Verify user email      response 200
        3. Auth user              response 200
        4. Refresh expired token  response 400
        5. Re-authorize           response 200
        6. Refresh refresh-token  response 200
        """
        # 1
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4
        await asyncio.sleep(settings.REFRESH_EXP_TIME)
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenExpiredHTTPException().detail

        # 5
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 6
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200

    async def test_5(self, client, session, redis, settings):
        """
        1. Create user        response 201
        2. Verify email user  response 200
        3. Auth user          response 200
        4. Refresh token      response 200
        5. Refresh old token  response 400
        """
        # 1
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200

        # 5
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenInvalidHTTPException().detail

    async def test_6(self, client, session, redis, settings):
        """
        1. Create user        response 201
        2. Verify email user  response 200
        3. Auth user          response 200
        4. Refresh token      response 200
        5. Refresh new token  response 200
        """
        # 1
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200

        # 5
        new_tokens = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=new_tokens.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200

    async def test_7(self, client, session, redis, settings):
        """
        1. Create user                         response 201
        2. Verify user email                   response 200
        3. Auth user                           response 200
        4. Logout user                         response 200
        5. Refresh token                       response 400
        6. Auth user                           response 200
        7. Refresh token                       response 200
        8. Logout user with old access-token   response 400
        9. Logout user with new access-token   response 200
        """
        # 1
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4
        token = JWTToken.model_validate_json(response.text)
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 200

        # 5
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenInvalidHTTPException().detail

        # 6
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 7
        token = JWTToken.model_validate_json(response.text)
        refresh_token = JWTRefreshToken(refresh_token=token.refresh_token)
        response = await refresh_handler(client, refresh_token)
        assert response.status_code == 200
        new_token = JWTToken.model_validate_json(response.text)

        # 8
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenInvalidHTTPException().detail

        # 9
        response = await logout_handler(client, new_token, new_token.access_token)
        assert response.status_code == 200
