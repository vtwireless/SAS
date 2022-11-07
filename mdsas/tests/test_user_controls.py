import json
import pytest
import logging

LOGGER = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Login Tests
# -------------------------------------------------------------------

def test_admin_login_without_payload(client):
    res = client.post('/adminLogin', json={})
    response = res.get_json()

    assert res.status_code == 200
    assert "status" in response
    assert response["status"] == 0
    assert "message" in response
    assert response["message"] == "Username or password not provided"

    LOGGER.debug(response)


def test_admin_login(client):
    res = client.post('/adminLogin', json={
        "username": "admin", "password": "admin"
    })
    response = res.get_json()
    LOGGER.debug(response)

    assert res.status_code == 200
    assert "status" in response
    assert "id" in response
    assert "name" in response
    assert "userType" in response
    assert response["status"] == 1
    assert response["id"] == 'admin'
    assert response["name"] == 'admin'
    assert response["userType"] == 'ADMIN'


def test_false_admin_login(client):
    res = client.post('/adminLogin', json={
        "username": "admin", "password": "IDONTKNOWTHEPASSWORD"
    })
    response = res.get_json()
    LOGGER.debug(response)

    assert res.status_code == 200
    assert "status" in response
    assert "message" in response
    assert response["message"] == "User could not be found"
    assert response["status"] == 1


# -------------------------------------------------------------------
# Create and Delete Users [Upto 50 users]
# -------------------------------------------------------------------

@pytest.mark.skip(reason="User not created")
def test_su_login(client):
    """
    Check if secondary user can log in
    """
    res = client.post('/suLogin', json={
        "username": "abc@abc.com",
        "password": "password"
    })
    print(json.loads(res.get_data(as_text=True)))
    assert res.status_code == 200
