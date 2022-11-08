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
        URL = f"http://{HOST}:{PORT}/{url}"

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
            assert response_item["cbsdId"] == 1

            assert "response" in response_item
            assert "responseCode" in response_item["response"]
            assert "responseMessage" in response_item["response"]

            if "availableChannel" in response_item:
                assert isinstance(response_item["availableChannel"], list)
                assert len(response_item["availableChannel"]) == 2

                available_channels = response_item["availableChannel"][0]
                assert "channelType" in available_channels
                assert "frequencyRange" in available_channels
                assert "maxEirp" in available_channels
                assert "ruleApplied" in available_channels

                assert "highFrequency" in available_channels["frequencyRange"]
                assert "lowFrequency" in available_channels["frequencyRange"]
            else:
                assert response_item["response"]["responseCode"] == "300"
                assert response_item["response"]["responseMessage"] == "UNSUPPORTED_SPECTRUM"

    def test_suLogin(self):
        response = self.send_request_to_server(HttpMethod.POST, 'suLogin')
        assert response.json()['status'] == 1

    def test_adminLogin(self):
        response = self.send_request_to_server(HttpMethod.POST, 'adminLogin')
        assert response.json()['status'] == 1
