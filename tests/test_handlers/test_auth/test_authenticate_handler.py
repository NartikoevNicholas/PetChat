import json

from jwt.utils import base64url_decode

from src.endpoints.exceptions import (
    UserNotFoundHTTPException,
    UnauthorizedHTTPException,
    TokenInvalidHTTPException,
    TokenTypeInvalidHTTPException,
    NeedEmailVerifyHTTPException,
)
from src.services.entities import (
    JWTToken,
    UserPasswordDTO,
    UserEmailPasswordDTO,
    UserUsernamePasswordDTO
)

from tests.test_handlers.utils import (
    get_user,
    get_code,
    get_user_id,
    auth_handler,
    logout_handler,
    delete_user_handler,
    registration_handler,
    verify_email_handler,
)


class TestAuthenticateHandler:
    async def test_1(self, client, session, redis, settings):
        """
        1. Create user              response 201
        2. Verify email user        response 200
        3. Auth user with username  response 200
        4. Auth user with email     response 200
        5. Check user_id            response True
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

        # 3. Auth user with username
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Auth user with email
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 5. Check user_id
        token = JWTToken.model_validate_json(response.text)
        header, payload, secret = token.access_token.split('.')
        payload = base64url_decode(payload).decode()
        assert payload.__contains__(user_id.hex) is True

    async def test_2(self, client, session, redis, settings):
        """
        1. Create user                     response 201
        2. Verify user email               response 200
        3. Auth user                       response 200
        4. logout user with refresh token  response 400
        5. logout user with access token   response 200
        6. logout user with access token   response 400
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

        # 3. Auth user with username
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. logout user with refresh token
        token = JWTToken.model_validate_json(response.text)
        response = await logout_handler(client, token, token.refresh_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenTypeInvalidHTTPException().detail

        # 5. logout user with access token
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 200

        # 6. logout user with access token
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == TokenInvalidHTTPException().detail

    async def test_3(self, client, session, redis, settings):
        """
        1. Create user               response 201
        2. Auth user with email      response 400
        3. Auth user with username   response 400
        4. Verify user email         response 200
        5. Auth user with email      response 200
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Auth user with email
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 400

        # 3. Auth user with username
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == NeedEmailVerifyHTTPException().detail

        # 4. Verify user email
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 5. Auth user with email
        login = UserEmailPasswordDTO(email=user.email, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

    async def test_4(self, client, session, redis, settings):
        """
        1. Create user                       response 201
        2. Verify user email                 response 200
        3. Auth user with another password   response 401
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

        # 3. Auth user with username
        login = UserUsernamePasswordDTO(username=user.username, password=f'{user.password}1')
        response = await auth_handler(client, login)
        assert response.status_code == 401
        assert json.loads(response.text)['detail'] == UnauthorizedHTTPException().detail

    async def test_5(self, client, session, redis, settings):
        """
        1. Create user         response 201
        2. Verify email user   response 200
        3. Auth user           response 200
        4. Delete user         response 204
        5. Auth user           response 400
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

        # 3. Auth user with username
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Delete user
        token = JWTToken.model_validate_json(response.text)
        user_password = UserPasswordDTO(password=user.password)
        response = await delete_user_handler(client, user_password, token.access_token)
        assert response.status_code == 204

        # 5. Check user_id
        response = await auth_handler(client, login)
        assert response.status_code == 400
        assert json.loads(response.text)['detail'] == UserNotFoundHTTPException().detail
