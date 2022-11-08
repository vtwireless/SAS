import pytest
import logging
from tests import conftest


class TestNodeCreation:
    LOGGER = logging.getLogger(__name__)

    def test_get_all_nodes(self, client):
        """ Get All Nodes """
        res = client.get("/getNodesRequest")
        response = res.get_json()
        self.LOGGER.debug(response)

        assert "status" in response
        assert "nodes" in response
        assert response["status"] == 1
        assert len(response["nodes"]) == 0
