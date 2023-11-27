import asyncio

from src.services.entities import (
    UserEmailDTO
)

from tests.test_handlers.utils import (
    get_user,
    registration_handler,
    available_handler
)


class TestAvailableUEmailHandler:
    async def test_1(self, client):
        """
        1. Check available correct email   response 200
        """
        # 1. Check available correct email
        user = get_user()
        user_email = UserEmailDTO(email=user.email)
        response = await available_handler(client, user_email)
        assert response.status_code == 200

    async def test_2(self, client):
        """
        1. Check available without content   response 200
        """
        # 1. Check available without content
        response = await available_handler(client)
        assert response.status_code == 422

    async def test_3(self, client):
        """
        1. Create user                 response 201
        2. Check available user.email  response 400
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Check available user.email
        user_email = UserEmailDTO(email=user.email)
        response = await available_handler(client, user_email)
        assert response.status_code == 400

    async def test_4(self, client, settings):
        """
        1. Create user                  response 201
        2. Check available user.email   response 400
        3. Sleep REG_EXP_TIME
        4. Check available user.email   response 200
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Check available user.username
        user_email = UserEmailDTO(email=user.email)
        response = await available_handler(client, user_email)
        assert response.status_code == 400

        # 3. Sleep ACCESS_EXP_TIME and 4. Check available user.email
        await asyncio.sleep(settings.REG_EXP_TIME)
        response = await available_handler(client, user_email)
        assert response.status_code == 200
