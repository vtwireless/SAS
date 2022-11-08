import pytest
import logging
from tests import conftest


class TestGrantCreation:
    LOGGER = logging.getLogger(__name__)

    def test_get_all_grants(self, client):
        """ Get All Grants """
        pytest.skip(conftest.not_implemented())
        res = client.get("/getGrantsRequest")
        response = res.get_json()

        self.LOGGER.info(response)
