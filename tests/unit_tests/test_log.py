def test_tags_list_endpoint(client):
    response = client.get(f"/", follow_redirects=True)
    assert response.status_code == 200


def test_tags_create_endpoint(client):
    data = {"name": "Naampje"}
    response = client.post(f"/", json=data, follow_redirects=True)
    assert response.status_code == 200
