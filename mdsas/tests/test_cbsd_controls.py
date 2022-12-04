import pytest
import logging
from tests import conftest


class TestCBSDCreation:
    LOGGER = logging.getLogger(__name__)

    def test_get_all_cbsds(self, client):
        """ Get All Nodes """
        res = client.get("/getNodesRequest")
        response = res.get_json()
        self.LOGGER.debug(response)

        assert "status" in response
        assert "nodes" in response
        assert response["status"] == 1
        assert len(response["nodes"]) == 0

    @pytest.mark.skip(conftest.fix_needed())
    def test_create_cbsds_without_data(self, client, data):
        payload = data["registrationRequest"]
        del payload["registrationRequest"][0]["nodeName"]

        res = client.post("/registrationRequest", json=payload)
        response = res.get_json()
        self.LOGGER.debug(response)

        conftest.check_standard_failure(
            "ErrorType: KeyError, Message: 'nodeName'", response
        )

    def test_create_cbsd(self, client, data):
        res = client.post("/registrationRequest", json=data["registrationRequest"])
        response = res.get_json()
        self.LOGGER.debug(response)

        conftest.check_standard_success(
            "Nodes have been added.", response
        )
        assert "registrationResponse" in response
        assert isinstance(response["registrationResponse"], list)
        assert len(response["registrationResponse"]) == 1

        for response_body in response["registrationResponse"]:
            conftest.check_winnforum_success(response_body)

    def test_get_all_cbsds_after_single_create(self, client):
        """ Get All Nodes """
        res = client.get("/getNodesRequest")
        response = res.get_json()
        self.LOGGER.debug(response)

        assert len(response["nodes"]) == 1

    def test_create_cbsds(self, client, data):
        res = client.post("/registrationRequest", json=data["registrationRequests"])
        response = res.get_json()
        self.LOGGER.debug(response)

        conftest.check_standard_success(
            "Nodes have been added.", response
        )
        assert "registrationResponse" in response
        assert isinstance(response["registrationResponse"], list)
        assert len(response["registrationResponse"]) == 2

        for response_body in response["registrationResponse"]:
            conftest.check_winnforum_success(response_body)

    def test_get_all_cbsds_after_multiple_create(self, client):
        """ Get All Nodes """
        res = client.get("/getNodesRequest")
        response = res.get_json()
        self.LOGGER.debug(response)

        assert len(response["nodes"]) == 3
        assert response["status"] == 1
