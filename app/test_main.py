from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_read_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_not_found():
    response = client.get("/made-up-route-that-clearly-doesnt-exist")
    print(response)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
