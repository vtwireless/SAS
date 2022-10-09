import json
import requests
from enum import Enum

POST_HEADERS, GET_HEADERS = {'Content-Type': 'application/json'}, {}
with open('test_data.json', 'r+') as infile:
    payloads = json.load(infile)


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'


def send_request_to_server(method: HttpMethod, url: str):
    URL = "http://localhost:8000/" + url
    response = None
    if method == HttpMethod.GET:
        response = requests.request("GET", URL, headers=GET_HEADERS, data={})

    elif method == HttpMethod.POST:
        response = requests.request("POST", URL, headers=POST_HEADERS, data=json.dumps(payloads[url]))

    return response


def test_getUsers():
    response = send_request_to_server(HttpMethod.GET, 'getUsers')
    assert response.json()['status'] == 1


def test_getUser():
    response = send_request_to_server(HttpMethod.POST, 'getUser')
    assert response.json()['status'] == 1


def test_spectrumInquiry():
    response = send_request_to_server(HttpMethod.POST, 'spectrumInquiryRequest')
    assert response.json()['status'] == 1
