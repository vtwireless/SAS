import json
import requests


def test_getUsers():
    url = "http://localhost:8000/getUsers"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)
    assert response.json()['status'] == 1


def test_getUser():
    url = "http://localhost:8000/getUser"

    payload = json.dumps({
        "username": "abc@abc.com",
        "password": "password"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    assert response.json()['status'] == 1


def test_spectrumInquiry():
    url = "http://localhost:8000/spectrumInquiryRequest"

    payload = json.dumps({
        "spectrumInquiryRequest": [
            {
                "cbsdId": 1,
                "inquiredSpectrum": [
                    {
                        "lowFrequency": 3550000000,
                        "highFrequency": 3560000000
                    }
                ]
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    assert response.json()['status'] == 1
