import asyncio

from tests.test_handlers.utils import (
    get_user,
    registration_handler
)


class TestRegistrationHandler:
    async def test_1(self, client):
        """
        1. Create user with success data   response 201
        """
        # 1. Create user with success data
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

    async def test_2(self, client):
        """
        1. Create user without username   response 422
        """
        # 1. Create user without username
        user = get_user(username=None)
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_3(self, client):
        """
        1. Create user short username   response 422
        """
        # 1. Create user short username
        user = get_user(username='test')
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_4(self, client):
        """
        1. Create user long username   response 422
        """
        # 1. Create user long username
        user = get_user(username='test' * 100)
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_5(self, client):
        """
        1. Create user without email   response 422
        """
        # 1. Create user long username
        user = get_user(email=None)
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_6(self, client):
        """
        1. Create user with invalid email   response 422
        """
        # 1. Create user with invalid email
        user = get_user(email='testtest')
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_7(self, client):
        """
        1. Create user without password   response 422
        """
        # 1. Create user without password
        user = get_user(password=None)
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_8(self, client):
        """
        1. Create user with short password   response 422
        """
        # 1. Create user with short password
        user = get_user(password='test')
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_9(self, client):
        """
        1. Create user with long password   response 422
        """
        # 1. Create user with short password
        user = get_user(password='test' * 100)
        response = await registration_handler(client, user)
        assert response.status_code == 422

    async def test_10(self, client):
        """
        1. Create user without is_superuser   response 201
        """
        # 1. Create user without is_superuser
        user = get_user(is_superuser=None)
        response = await registration_handler(client, user)
        assert response.status_code == 201

    async def test_11(self, client):
        """
        1. Create user with is_superuser=False   response 201
        """
        # 1. Create user with is_superuser=False
        user = get_user(is_superuser=False)
        response = await registration_handler(client, user)
        assert response.status_code == 201

    async def test_12(self, client):
        """
        1. Create user with is_superuser=True   response 201
        """
        # 1. Create user with is_superuser=True
        user = get_user(is_superuser=True)
        response = await registration_handler(client, user)
        assert response.status_code == 201

    async def test_13(self, client):
        """
        1. Create user1   response 201
        2. Create user2 with email=user1.email   response 400
        """
        # 1. Create user1
        user1 = get_user(username='testtest1')
        response = await registration_handler(client, user1)
        assert response.status_code == 201

        # 2. Create user2 with email=user1.email
        user2 = get_user(username='testtest2')
        response = await registration_handler(client, user2)
        assert response.status_code == 400

    async def test_14(self, client):
        """
        1. Create user1   response 201
        2. Create user2 with username=user1.username   response 400
        """
        # 1. Create user1
        user1 = get_user(email='test1@yandex.ru')
        response = await registration_handler(client, user1)
        assert response.status_code == 201

        # 2. Create user2 with username=user1.username
        user2 = get_user(email='test2@yandex.ru')
        response = await registration_handler(client, user2)
        assert response.status_code == 400

    async def test_15(self, client, settings):
        """
        1. Create user          response 201
        2. Create user          response 400
        3. Sleep REG_EXP_TIME
        4. Create user          response 201
        """
        # 1. Create user
        user = get_user()
        response = await registration_handler(client, user)
        assert response.status_code == 201

        # 2. Create user
        response = await registration_handler(client, user)
        assert response.status_code == 400

        # 3. Sleep REG_EXP_TIME and 4. Create user
        await asyncio.sleep(settings.REG_EXP_TIME)
        response = await registration_handler(client, user)
        assert response.status_code == 201
