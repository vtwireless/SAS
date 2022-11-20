import logging
from tests import conftest


class TestUserLoginMethods:
    LOGGER = logging.getLogger(__name__)

    def test_admin_login_without_payload(self, client):
        res = client.post('/adminLogin', json={})
        response = res.get_json()

        assert res.status_code == 200
        conftest.check_standard_failure("Username or password not provided", response)

        self.LOGGER.debug(response)

    def test_admin_login(self, client):
        res = client.post('/adminLogin', json={
            "username": "admin", "password": "admin"
        })
        response = res.get_json()
        self.LOGGER.debug(response)

        assert res.status_code == 200
        assert "status" in response
        assert "id" in response
        assert "name" in response
        assert "userType" in response
        assert response["status"] == 1
        assert response["id"] == 'admin'
        assert response["name"] == 'admin'
        assert response["userType"] == 'ADMIN'

    def test_false_admin_login(self, client):
        res = client.post('/adminLogin', json={
            "username": "admin", "password": "IDONTKNOWTHEPASSWORD"
        })
        response = res.get_json()
        self.LOGGER.debug(response)

        assert res.status_code == 200
        conftest.check_standard_failure("User could not be found", response)

    def test_su_login(self, client):
        """
        Check if secondary user can log in
        """
        res = client.post('/suLogin', json={
            "username": "abc@abc.com",
            "password": "password"
        })
        response = res.get_json()
        self.LOGGER.debug(response)

        assert res.status_code == 200
        for key in ['id', 'name', 'status', 'userType']:
            assert key in response

        assert response["status"] == 1
        assert response["userType"] == 'SU'
