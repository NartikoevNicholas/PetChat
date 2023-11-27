import json
from httpx import AsyncClient

from src.core.config import API


class TestHealthHandler:
    async def test_ping_app(
        self,
        client: AsyncClient
    ):
        response = await client.get(url=API.health_ping_app_v1)
        assert response.status_code == 200
        assert json.loads(response.text)['message'] == 'Application worked!'

    async def test_ping_db(
        self,
        client: AsyncClient
    ):
        response = await client.get(url=API.health_ping_db_v1)
        assert response.status_code == 200
        assert json.loads(response.text)['message'] == 'Database worked!'

    async def test_ping_mem_cache(
        self,
        client: AsyncClient
    ):
        response = await client.get(url=API.health_ping_memory_cache_v1)
        assert response.status_code == 200
        assert json.loads(response.text)['message'] == 'Memory cache worked!'
