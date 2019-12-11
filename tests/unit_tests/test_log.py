def test_get_log_endpoint(client):
    response = client.get(f"/", follow_redirects=True)
    assert response.status_code == 200
    # Todo: assert template + DB

#
# def test_post_log_endpoint(client):
#     response = client.post(f"/")
#     assert response.status_code == 200
#     # Todo: assert template + DB

