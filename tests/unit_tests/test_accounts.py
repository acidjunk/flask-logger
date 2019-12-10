from tests.unit_tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD
from tests.unit_tests.helpers import login, logout


def test_admin_login(client, admin):
    """Make sure login and logout works."""
    response = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    print(response)
    assert response.json["response"]["user"]["authentication_token"]
    assert response.status_code == 200
    logout(client)

    response = login(client, ADMIN_EMAIL, "Wrong password")
    assert response.status_code == 400
    assert response.json["response"]["errors"]["password"] == ["Invalid password"]


def test_unconfirmed_admin_login(client, admin_unconfirmed):
    """Make sure login shows confirmation error."""
    response = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    assert response.json["response"]["errors"]["email"][0] == "Email requires confirmation."
    assert response.status_code == 400
