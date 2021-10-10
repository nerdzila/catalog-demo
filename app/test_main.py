import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import security
from .main import app, get_db
from .database import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "pwd"

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


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture()
def users_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        hashed_password = security.get_password_hash(
            TEST_USER_PASSWORD
        )
        conn.execute(
            """
                INSERT INTO
                    users(email, hashed_password, is_admin)
                    VALUES(:email, :pwd, :is_admin)
            """,
            email=TEST_USER_EMAIL,
            pwd=hashed_password,
            is_admin=True
        )

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(users_db):
    token = security.create_access_token(
        data={"sub": TEST_USER_EMAIL}
    )
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def test_read_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_not_found():
    response = client.get("/made-up-route-that-clearly-doesnt-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_token_with_proper_credentials(users_db):
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }

    response = client.post('/token', data=login_data)

    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_token_with_wrong_credentials(users_db):
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": 'another_password'
    }

    response = client.post('/token', data=login_data)
    assert response.status_code == 401
    assert {'detail': "Could not validate credentials"}

    login_data = {
        "username": 'Another User',
        "password": TEST_USER_PASSWORD
    }

    response = client.post('/token', data=login_data)
    assert response.status_code == 401
    assert {'detail': "Could not validate credentials"}


def test_authentication_with_bad_token(users_db):
    headers = {"Authorization": "Bearer complete_n0n_s3ns3"}
    response = client.get("/users/", headers=headers)

    assert response.status_code == 401


def test_authentication_error_with_deleted_user(users_db, auth_headers):
    response = client.delete('/users/1', headers=auth_headers)

    assert response.status_code == 200

    response = client.get("/users/", headers=auth_headers)
    assert response.status_code == 401
    assert {'detail': "Could not validate credentials"}


def test_get_all_users(users_db, auth_headers):
    response = client.get("/users/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "email": "test@example.com",
                               "is_admin": True}]


def test_user_get_by_id(users_db, auth_headers):
    response = client.get("/users/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "email": "test@example.com",
                               "is_admin": True}


def test_user_get_by_id_that_doesnt_exist(users_db, auth_headers):
    response = client.get("/users/11111111111111111", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_user_creation(users_db, auth_headers):
    response = client.post(
        "/users/",
        headers=auth_headers,
        json=dict(
            email="test_2@example.com",
            is_admin=True,
            password="not a real password"
        )
    )
    assert response.status_code == 200
    assert response.json() == {"id": 2, "email": "test_2@example.com",
                               "is_admin": True}

    response = client.get("/users/", headers=auth_headers)
    assert len(response.json()) == 2


def test_user_creation_duplicate_user(users_db, auth_headers):
    response = client.post(
        "/users/",
        headers=auth_headers,
        json=dict(
            email="test@example.com",
            is_admin=True,
            password="not a real password"
        )
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


def test_user_update(users_db, auth_headers):
    new_email = "test_new@example.com"
    new_password = "test_new@example.com"
    response = client.put(
        "/users/1",
        headers=auth_headers,
        json=dict(
            email=new_email,
            is_admin=False,
            password=new_password
        )
    )

    expected_user = {"id": 1, "email": new_email, "is_admin": False}

    assert response.status_code == 200
    assert response.json() == expected_user

    # Up to this point we know that the request was successful
    # but we also have to check that the password update happened
    # by authenticating with the new password
    login_data = {"username": new_email, "password": new_password}
    response = client.post('/token', data=login_data)

    assert response.status_code == 200

    token = response.json()
    new_headers = {"Authorization": f"Bearer {token['access_token']}"}

    # We also check that getting the user by ID returns the same
    # content as the update request
    response = client.get('users/1', headers=new_headers)
    assert response.json() == expected_user


def test_user_update_unknown_user(users_db, auth_headers):
    response = client.put(
        "/users/111111111111",
        headers=auth_headers,
        json=dict(
            email="test_new@example.com",
            is_admin=False,
            password="new_password"
        )
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User doesn't exist"}


def test_user_deletion(users_db, auth_headers):
    response = client.post(
        "/users/",
        headers=auth_headers,
        json=dict(
            email="test_2@example.com",
            is_admin=True,
            password="not a real password"
        )
    )
    assert response.status_code == 200

    response = client.get("/users/", headers=auth_headers)
    assert len(response.json()) == 2

    response = client.delete("/users/2", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"id": 2}

    response = client.get("/users/", headers=auth_headers)
    assert len(response.json()) == 1


def test_user_delete_unknown_user(users_db, auth_headers):
    response = client.delete("/users/11111", headers=auth_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "User doesn't exist"}
