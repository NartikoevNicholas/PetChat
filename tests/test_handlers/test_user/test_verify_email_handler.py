import uuid

from tests.test_handlers.utils import (
    get_user,
    get_user_id,
    get_code,
    registration_handler,
    verify_email_handler,
)


class TestVerifyEmailHandler:
    async def test_1(self, client, session, redis, settings):
        """
        1. Create user         response 201
        2. Verify user email   response 200
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

    async def test_2(self, client, session, redis, settings):
        """
        1. Create user                           response 201
        2. Verify user email with another uuid   response 400
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Verify user email with another uuid
        user_id = await get_user_id(session, user.username)
        code = await get_code(redis, settings, user_id)
        response = await verify_email_handler(client, uuid.uuid4(), code)
        assert response.status_code == 400

    async def test_3(self, client, session, redis, settings):
        """
        1. Create user            response 201
        2. Verify user email      response 200
        3. Re-verify user email   response 400
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

        # 3. Re-verify user email
        response = await verify_email_handler(client, user_id, code)
        assert response.status_code == 400
