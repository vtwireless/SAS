import json


def test_index(client):
    res = client.get('/getUsers')
    assert res.status_code == 200

    response = json.loads(res.get_data(as_text=True))
    assert "status" in response
    assert response["status"] == 1


def test_get_single_user(client):
    res = client.post('/getUser', json={
        "username": "abc@abc.com",
        "password": "password"
    })
    print(json.loads(res.get_data(as_text=True)))
    assert res.status_code == 200
