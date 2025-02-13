import time

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.router.main import app
from app.router.ch5.router import add

client = TestClient(app)

def test_ch5_add():
    assert add(10.1, 20) == 30.1
    assert add(10.1, 20) != 30.11
    assert add(10, -20) == -10.0


def test_ch5_list():
    response = client.get(f'/ch5/list')
    assert response.status_code == 200
    assert response.json() == {'offset': 0, 'limit': 10}

    response = client.get(f'/ch5/list?offset=10&limit=10')
    assert response.status_code == 200
    assert response.json() == {'offset': 10, 'limit': 10}

    response = client.get(f'/ch5/list?offset=10&limit=10')
    assert response.status_code == 200
    assert response.json() != {'offset': 0, 'limit': 0}


@pytest.mark.asyncio
async def test_ch5_async_1():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost:8888') as ac:
        task1 = ac.get('/ch5/async_1')
        task2 = ac.get('/ch5/async_2')
        s = time.time()
        responses = await asyncio.gather(task1, task2)
        print(time.time() - s)

    assert responses[0].status_code == 200
    assert responses[0].json() == {}

    assert responses[1].status_code == 200
    assert responses[1].json() == {}
