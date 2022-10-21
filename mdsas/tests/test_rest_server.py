import json
import requests
from enum import Enum

POST_HEADERS, GET_HEADERS = {'Content-Type': 'application/json'}, {}
HOST, PORT = 'localhost', 8000

with open('test_data.json', 'r+') as infile:
    payloads = json.load(infile)


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'


class TestRestServer:
    
    @staticmethod
    def send_request_to_server(method: HttpMethod, url: str):
        URL = f"http://{HOST}:{PORT}/" + url
        response = None
        if method == HttpMethod.GET:
            response = requests.request("GET", URL, headers=GET_HEADERS, data={})

        elif method == HttpMethod.POST:
            response = requests.request("POST", URL, headers=POST_HEADERS, data=json.dumps(payloads[url]))

        return response
    
    def test_getUsers(self):
        response = self.send_request_to_server(HttpMethod.GET, 'getUsers')
        assert response.json()['status'] == 1

    def test_getUser(self):
        response = self.send_request_to_server(HttpMethod.POST, 'getUser')
        assert response.json()['status'] == 1

    def test_spectrumInquiry(self):
        response = self.send_request_to_server(HttpMethod.POST, 'spectrumInquiryRequest')
        response_json = response.json()

        assert response_json['status'] == 1
        assert "spectrumInquiryResponse" in response_json
        assert len(response_json["spectrumInquiryResponse"]) == 2
        for response_item in response_json["spectrumInquiryResponse"]:
            assert "cbsdId" in response_item
            assert "response" in response_item
            assert "responseCode" in response_item["response"]
            assert "responseMessage" in response_item["response"]

    def test_suLogin(self):
        response = self.send_request_to_server(HttpMethod.POST, 'suLogin')
        assert response.json()['status'] == 1

    def test_adminLogin(self):
        response = self.send_request_to_server(HttpMethod.POST, 'adminLogin')
        assert response.json()['status'] == 1
