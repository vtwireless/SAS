import pytest
import logging
from tests import conftest


class TestNodeCreation:
    LOGGER = logging.getLogger(__name__)

    def test_get_all_nodes(self, client):
        """ Get All Nodes """
        pytest.skip(conftest.not_implemented())
        res = client.get("/getNodesRequest")
        response = res.get_json()

        self.LOGGER.info(response)
