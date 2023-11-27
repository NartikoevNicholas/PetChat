from src.services.entities import (
    JWTToken,
    UserResponseDTO,
    UserPasswordDTO,
    UserUpdatePassword,
    UserEmailPasswordDTO,
    UserUsernamePasswordDTO,
)

from tests.test_handlers.utils import (
    get_user,
    get_code,
    get_user_id,
    me_handler,
    auth_handler,
    logout_handler,
    update_user_handler,
    delete_user_handler,
    registration_handler,
    verify_email_handler,
)


class TestUserUpdateHandler:
    async def test_1(self, client, session, redis, settings):
        """
        1. Create user         response 201
        2. Verify email user   response 200
        3. Auth user           response 200
        4. Update username     response 200
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify email user
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Update username
        token = JWTToken.model_validate_json(response.text)
        user_patch = UserUsernamePasswordDTO(username=user.username * 2, password=user.password)
        response = await update_user_handler(client, user_patch, token.access_token)
        assert response.status_code == 200
        user_update = UserResponseDTO.model_validate_json(response.text)
        assert user_update.username == user_patch.username

    async def test_2(self, client, session, redis, settings):
        """
        1. Create user         response 201
        2. Verify email user   response 200
        3. Auth user           response 200
        4. Update email        response 200
        5. Verify email        response 200
        6. Get me              response 200
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify email user
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Update email
        token = JWTToken.model_validate_json(response.text)
        user_patch = UserEmailPasswordDTO(email='test_test@yandex.ru', password=user.password)
        response = await update_user_handler(client, user_patch, token.access_token)
        assert response.status_code == 200
        user_update = UserResponseDTO.model_validate_json(response.text)
        assert user_update.email == user.email

        # 5.Verify email
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 6. Get me
        response = await me_handler(client, token.access_token)
        assert response.status_code == 200
        user_update = UserResponseDTO.model_validate_json(response.text)
        assert user_update.email == user_patch.email

    async def test_3(self, client, session, redis, settings):
        """
        1. Create user         response 201
        2. Verify email user   response 200
        3. Auth user           response 200
        4. Update password     response 200
        5. Logout user         response 200
        6. Auth user           response 200
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify email user
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Update username
        token = JWTToken.model_validate_json(response.text)
        user_patch = UserUpdatePassword(new_password=user.password * 2, password=user.password)
        response = await update_user_handler(client, user_patch, token.access_token)
        assert response.status_code == 200

        # 5. Logout user
        response = await logout_handler(client, token, token.access_token)
        assert response.status_code == 200

        # 6. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user_patch.new_password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

    async def test_4(self, client, session, redis, settings):
        """
        1. Create user         response 201
        2. Verify email user   response 200
        3. Auth user           response 200
        4. Delete user         response 204
        5. Update username     response 400
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify email user
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 200

        # 3. Auth user
        login = UserUsernamePasswordDTO(username=user.username, password=user.password)
        response = await auth_handler(client, login)
        assert response.status_code == 200

        # 4. Delete user
        token = JWTToken.model_validate_json(response.text)
        user_password = UserPasswordDTO(password=user.password)
        response = await delete_user_handler(client, user_password, token.access_token)
        assert response.status_code == 204

        # 5. Update username
        user_patch = UserUsernamePasswordDTO(username=user.username * 2, password=user.password)
        response = await update_user_handler(client, user_patch, token.access_token)
        assert response.status_code == 400
