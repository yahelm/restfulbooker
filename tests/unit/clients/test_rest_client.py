import pytest
import responses
from requests.auth import HTTPBasicAuth

from restfulbooker.clients.auth import TokenAuth
from restfulbooker.clients.rest_client import RestClient

BASE_URL = "https://api.test"


@pytest.mark.parametrize(
    ("base_url", "path"),
    [
        ("https://api.test", "/booking"),
        ("https://api.test", "booking"),
        ("https://api.test/", "/booking"),
    ],
)
def test_url_joins_base_url_and_path(
    mocked_responses: responses.RequestsMock, base_url: str, path: str
) -> None:
    mocked_responses.get(f"{BASE_URL}/booking")

    response = RestClient(base_url, timeout=5).get(path)

    assert response.request.url == f"{BASE_URL}/booking"


@pytest.mark.parametrize("status", [404, 500])
def test_error_status_returns_response(
    mocked_responses: responses.RequestsMock, status: int
) -> None:
    mocked_responses.get(f"{BASE_URL}/booking/1", status=status)

    response = RestClient(BASE_URL, timeout=5).get("/booking/1")

    assert response.status_code == status


def test_auth_is_passed_to_request(mocked_responses: responses.RequestsMock) -> None:
    mocked_responses.delete(f"{BASE_URL}/booking/1", status=201)

    response = RestClient(BASE_URL, timeout=5).delete(
        "/booking/1", auth=HTTPBasicAuth("admin", "secret")
    )

    assert response.request.headers["Authorization"].startswith("Basic ")


def test_token_auth_sets_cookie(mocked_responses: responses.RequestsMock) -> None:
    mocked_responses.patch(f"{BASE_URL}/booking/1")

    response = RestClient(BASE_URL, timeout=5).patch(
        "/booking/1", auth=TokenAuth("abc123")
    )

    assert response.request.headers["Cookie"] == "token=abc123"
