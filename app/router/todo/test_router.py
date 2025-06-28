import random
import string
from fastapi.testclient import TestClient

from app.router.main import app

name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
token = None
todos = []


def test_signup():
    with TestClient(app) as client:
        resp = client.post('/todo/users/signup', json={'email': f'{name}@gmail.com', 'password': '1234'})
        assert resp.status_code == 200

        resp = client.post('/todo/users/signup', json={'email': f'{name}@gmail.com', 'password': '1234'})
        assert resp.status_code == 400


def test_signin():
    with TestClient(app) as client:
        resp = client.post('/todo/users/signin', json={'email': f'{name}{name}@gmail.com', 'password': '1234'})
        assert resp.status_code == 400

        resp = client.post('/todo/users/signin', json={'email': f'{name}@gmail.com', 'password': '12345'})
        assert resp.status_code == 400

        resp = client.post('/todo/users/signin', json={'email': f'{name}@gmail.com', 'password': '1234'})
        assert resp.status_code == 200

        global token
        token = resp.json()['x_access_token']
        assert token is not None


def test_add_todo():
    global token
    with TestClient(app) as client:
        resp = client.post(
            '/todo',
            json={'title': 'title', 'content': 'content', 'created_at': '2025-05-01 11:11:11'},
            headers={'x-access-token': ''}
        )
        assert resp.status_code == 403

        resp = client.post(
            '/todo',
            json={'title': 'title', 'content': 'content', 'created_at': '2025-05-01 11:11:11'},
            headers={'x-access-token': token}
        )
        assert resp.status_code == 200

        resp = client.post(
            '/todo',
            json={'title': 'title', 'content': 'content', 'created_at': '2025-05-01 12:12:12'},
            headers={'x-access-token': token}
        )
        assert resp.status_code == 200

        resp = client.post(
            '/todo',
            json={'title': 'title', 'content': 'content', 'created_at': '2025-05-01 13:13:13'},
            headers={'x-access-token': token}
        )
        assert resp.status_code == 200


def test_get_todo_list():
    global token
    global todos
    with TestClient(app) as client:
        resp = client.get('/todo?start=2025-05-01&end=2025-05-02', headers={'x-access-token': ''})
        assert resp.status_code == 403

        resp = client.get('/todo?start=2025-05-01&end=2025-05-02', headers={'x-access-token': token})
        assert resp.status_code == 200

        todos = resp.json()['todos']
        assert len(todos) == 3

        resp = client.get('/todo?start=2025-05-02&end=2025-05-03', headers={'x-access-token': token})
        assert resp.status_code == 200
        assert len(resp.json()['todos']) == 0


def test_get_todo():
    global token
    global todos
    with TestClient(app) as client:
        resp = client.get(f'/todo/9999', headers={'x-access-token': ''})
        assert resp.status_code == 403

        resp = client.get(f'/todo/9999', headers={'x-access-token': token})
        assert resp.status_code == 400

        for todo in todos:
            resp = client.get(f'/todo/{todo["id"]}', headers={'x-access-token': token})
            assert resp.status_code == 200
            assert resp.json()['todo']['id'] == todo['id']


def test_complete_todo():
    global token
    global todos
    with TestClient(app) as client:
        resp = client.patch(f'/todo/9999/complete', headers={'x-access-token': ''})
        assert resp.status_code == 403

        resp = client.patch(f'/todo/{todos[0]["id"]}/complete', headers={'x-access-token': token})
        assert resp.status_code == 200

        resp = client.get(f'/todo/{todos[0]["id"]}', headers={'x-access-token': token})
        assert resp.status_code == 200
        assert resp.json()['todo']['completed_at'] is not None


def test_delete_todo():
    global token
    global todos
    with TestClient(app) as client:
        for todo in todos:
            resp = client.delete(f'/todo/{todo["id"]}', headers={'x-access-token': token})
            assert resp.status_code == 200

            resp = client.get(f'/todo/{todo["id"]}', headers={'x-access-token': token})
            assert resp.status_code == 400
