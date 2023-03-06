import logging
from seed_renderer import HttpMethod, Client
import json

if __name__ == '__main__':
    client = Client('data_assets/nrdz_demo.json')
    logging.basicConfig()
    logger = logging.getLogger("nrdz_demo")
    logger.setLevel(logging.DEBUG)

    logger.info("Creating a new user")
    res = client.send_request_to_server(HttpMethod.POST, 'createSU')
    print(json.dumps(res.json(), indent=4))

    logger.info("Adding 3 nodes [2 at HCRO and 1 at BB]")
    res = client.send_request_to_server(HttpMethod.POST, 'registrationRequest')
    print(json.dumps(res.json(), indent=4))

    logger.info("Sending Grant Requests")
    res = client.send_request_to_server(HttpMethod.POST, 'grantRequest')
    print(json.dumps(res.json(), indent=4))


