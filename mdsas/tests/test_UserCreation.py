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

    @pytest.mark.skip(conftest.fix_needed())
    def test_check_email_availability_when_user_exists(self, client, data):
        """
        Check if an email is available for use by a secondary user when another user already uses it.
        """
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
        res = client.get("/getUsers")
        response = res.get_json()

        assert res.status_code == 200
        assert "status" in response
        assert response["status"] == 1

        assert "secondaryUsers" in response
        assert isinstance(response["secondaryUsers"], list)
        assert len(response["secondaryUsers"]) == 4

        self.LOGGER.debug(response)
