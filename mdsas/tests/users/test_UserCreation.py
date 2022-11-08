import pytest
import logging
from tests import conftest


class TestUserCreation:
    LOGGER = logging.getLogger(__name__)

    def test_create_bad_secondary_user(self, client, data):
        """
        Check response in case of incorrect or missing fields
        """

        payload = data["createSU"]
        del payload["secondaryUserEmail"]
        self.LOGGER.debug(payload)

        res = client.post('/createSU', json=payload)
        response = res.get_json()

        assert res.status_code == 200
        conftest.check_standard_failure("ErrorType: KeyError, Message: 'secondaryUserEmail'", response)

        self.LOGGER.debug(response)

    def test_check_email_availability(self, client, data):
        """
        Check if an email is available for use by a secondary user
        """

        payload = data["createSU"]
        self.LOGGER.debug(payload)

        res = client.post('/checkEmailAvail', json={
            "email": payload["secondaryUserEmail"]
        })
        response = res.get_json()

        assert res.status_code == 200
        conftest.check_standard_success('Email Unique', response)
        assert "exists" in response
        assert response["exists"] == 0

        self.LOGGER.debug(response)

    def test_create_secondary_user(self, client, data):
        """
        Check response while creating secondary user
        """

        payload = data["createSU"]
        self.LOGGER.debug(payload)

        res = client.post('/createSU', json=payload)
        response = res.get_json()

        assert res.status_code == 200
        conftest.check_standard_success('User has been added.', response)

        self.LOGGER.debug(response)

    def test_check_email_availability_when_user_exists(self, client, data):
        """
        Check if an email is available for use by a secondary user when another user already uses it.
        """
        pytest.skip(conftest.fix_needed())
        payload = data["createSU"]
        self.LOGGER.debug(payload)

        res = client.post('/checkEmailAvail', json={
            "email": payload["secondaryUserEmail"]
        })
        response = res.get_json()

        assert res.status_code == 200
        conftest.check_standard_success('Email In Use', response)
        assert "exists" in response
        assert response["exists"] == 1

        self.LOGGER.info(response)

    def test_create_another_user_with_same_details(self, client, data):
        """
        Check response while creating secondary user
        """

        payload = data["createSU"]
        self.LOGGER.debug(payload)

        res = client.post('/createSU', json=payload)
        response = res.get_json()

        assert res.status_code == 200
        conftest.check_standard_failure(
            "Email 'abc@abc.com' already exists. Contact an administrator to recover or reset password.",
            response
        )
        assert "exists" in response
        assert response["exists"] == 1

        self.LOGGER.debug(response)

    def test_create_multiple_users(self, client, data):
        """
        Check response while creating several secondary users
        """

        payloads = data["createSUs"]
        for payload in payloads:
            self.LOGGER.debug(payload)

            res = client.post('/createSU', json=payload)
            response = res.get_json()

            assert res.status_code == 200
            conftest.check_standard_success('User has been added.', response)

            self.LOGGER.debug(response)

    def test_get_all_users(self, client):
        """ Get All Users """
        pytest.skip(conftest.not_implemented())
        res = client.get("/getUsers")
        response = res.get_json()

        self.LOGGER.info(response)

    def test_su_login(self, client):
        """
        Check if secondary user can log in
        """
        pytest.skip(conftest.not_implemented())
        res = client.post('/suLogin', json={
            "username": "abc@abc.com",
            "password": "password"
        })
        response = res.get_json()
        self.LOGGER.debug(response)

        assert res.status_code == 200
