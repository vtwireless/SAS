import json
import requests
from enum import Enum


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'


class Client:
    POST_HEADERS, GET_HEADERS = {'Content-Type': 'application/json'}, {}
    HOST, PORT = 'localhost', 8000
    ASSETS = 'data_assets/seed_data.json'
    payloads = None

    def __init__(self):
        with open(self.ASSETS, 'r+') as infile:
            self.payloads = json.load(infile)

    def send_request_to_server(self, method: HttpMethod, url: str, payloadUrl=None):
        URL = f"http://{self.HOST}:{self.PORT}/{url}"

        response = None
        if method == HttpMethod.GET:
            response = requests.request("GET", URL, headers=self.GET_HEADERS, data={})

        elif method == HttpMethod.POST:
            if not payloadUrl:
                payloadUrl = url
            response = requests.request(
                "POST", URL, headers=self.POST_HEADERS, data=json.dumps(self.payloads[payloadUrl])
            )

        return response


if __name__ == '__main__':
    client = Client()

    # Create Users
    res = client.send_request_to_server(HttpMethod.POST, 'createSU')
    print(res)
    # res = client.send_request_to_server(HttpMethod.POST, 'createSU', 'createSUs')
    # print(res)

    # Add Nodes
    res = client.send_request_to_server(HttpMethod.POST, 'registrationRequest')
    print(res)
    # res = client.send_request_to_server(HttpMethod.POST, 'registrationRequest', 'registrationRequests')
    # print(res)

    # Spectrum Inquiry
    res = client.send_request_to_server(HttpMethod.POST, 'spectrumInquiryRequest')
    print(res)

    # Grant Request
    res = client.send_request_to_server(HttpMethod.POST, 'grantRequest')
    print(res)



