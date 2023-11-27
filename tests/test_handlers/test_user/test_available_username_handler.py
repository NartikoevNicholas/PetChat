import asyncio

from src.services.entities import (
    UserUsernameDTO
)

from tests.test_handlers.utils import (
    get_user,
    registration_handler,
    available_handler
)


class TestAvailableUsernameHandler:

    async def test_1(self, client):
        """
        1. Check available username   response 200
        """
        # 1. Check available username
        user = get_user()
        user_username = UserUsernameDTO(username=user.username)
        response = await available_handler(client, user_username)
        assert response.status_code == 200

    async def test_2(self, client):
        """
        1. Check available username without content  response 422
        """
        response = await available_handler(client)
        assert response.status_code == 422

    async def test_3(self, client):
        """
        1. Create user                     response 201
        2. Check available user.username   response 400
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2 Check available user.username
        user_username = UserUsernameDTO(username=user.username)
        response = await available_handler(client, user_username)
        assert response.status_code == 400

    async def test_4(self, client, settings):
        """
        1. Create user                     response 201
        2. Check available user.username   response 400
        3. Sleep REG_EXP_TIME
        4. Check available user.username   response 200
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Check available user.username
        user_username = UserUsernameDTO(username=user.username)
        response = await available_handler(client, user_username)
        assert response.status_code == 400

        # 3. Sleep ACCESS_EXP_TIME and 4. Check available user.username
        await asyncio.sleep(settings.REG_EXP_TIME)
        response = await available_handler(client, user_username)
        assert response.status_code == 200
