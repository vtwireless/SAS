import pytest
import logging
from tests import conftest


class TestGrantCreation:
    LOGGER = logging.getLogger(__name__)

    def test_get_all_grants(self, client):
        """ Get All Grants """
        res = client.get("/getGrantsRequest")
        response = res.get_json()
        self.LOGGER.debug(response)

        assert "status" in response
        assert "spectrumGrants" in response
        assert response["status"] == 1
        assert len(response["spectrumGrants"]) == 0
