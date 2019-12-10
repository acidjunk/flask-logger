def test_tags_list_endpoint(client, tag_1):
    response = client.get(f"/v1/tags", follow_redirects=True)
    assert response.status_code == 403


def test_tags_create_endpoint(client):
    data = {"name": "Naampje"}
    response = client.post(f"/v1/tags", json=data, follow_redirects=True)
    assert response.status_code == 403
