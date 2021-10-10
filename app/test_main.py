import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .main import app, get_db
from .database import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False,
                                   bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def users_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(
            "INSERT INTO users VALUES(1, 'test@example.com', 'hash', 1)"
        )

    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_read_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_not_found():
    response = client.get("/made-up-route-that-clearly-doesnt-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_get_all_users(users_db):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "email": "test@example.com",
                               "is_admin": True}]


def test_user_get_by_id(users_db):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "email": "test@example.com",
                               "is_admin": True}


def test_user_get_by_id_that_doesnt_exist(users_db):
    response = client.get("/users/11111111111111111")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_user_creation(users_db):
    response = client.post("/users/", json=dict(
        email="test_2@example.com",
        is_admin=True,
        password="not a real password"
    ))
    assert response.status_code == 200
    assert response.json() == {"id": 2, "email": "test_2@example.com",
                               "is_admin": True}

    response = client.get("/users/")
    assert len(response.json()) == 2


def test_user_creation_duplicate_user(users_db):
    response = client.post("/users/", json=dict(
        email="test@example.com",
        is_admin=True,
        password="not a real password"
    ))
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


def test_user_update(users_db):
    response = client.put("/users/1", json=dict(
        email="test_new@example.com",
        is_admin=False,
        password="new_password"
    ))

    expected_user = {"id": 1, "email": "test_new@example.com",
                     "is_admin": False}

    assert response.status_code == 200
    assert response.json() == expected_user

    response = client.get('users/1')

    assert response.json() == expected_user


def test_user_update_unknown_user(users_db):
    response = client.put("/users/111111111111", json=dict(
        email="test_new@example.com",
        is_admin=False,
        password="new_password"
    ))

    assert response.status_code == 404
    assert response.json() == {"detail": "User doesn't exist"}
