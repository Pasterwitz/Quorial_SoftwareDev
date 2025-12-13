from sqlite3 import IntegrityError
from unittest.mock import MagicMock
from unittest.mock import patch
from flask.testing import FlaskClient
 
 
def test_get_404(client: FlaskClient) -> None:
    assert client.get("/does-not-exist").status_code == 404
 
 
def test_get_register(client: FlaskClient) -> None:
    assert client.get("/auth/register").status_code == 200
 
 
def test_post_register_no_input(client: FlaskClient) -> None:
    assert client.post("/auth/register").status_code == 400
 
 
def test_post_register_successfully(client: FlaskClient) -> None:
    db = MagicMock()
 
    with patch("flask_quorial.auth.get_db", return_value=db):
        response = client.post(
            "/auth/register",
            data={
                "username": "test-user",
                "password": "1234",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
 
 
def test_post_register_already_registered(client: FlaskClient) -> None:
    db = MagicMock()
    db.commit = MagicMock(side_effect=IntegrityError)
 
    with patch("flask_quorial.auth.get_db", return_value=db):
        username = "test-user"
        response = client.post(
            "/auth/register",
            data={
                "username": username,
                "password": "1234",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert f"User {username} is already registered." in response.data.decode()
 