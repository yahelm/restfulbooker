import pytest
import requests
import responses

from restfulbooker.clients.healthcheck import check_health
from restfulbooker.config import Settings

BASE_URL = "https://api.test"
PING_URL = f"{BASE_URL}/ping"


@pytest.fixture
def settings() -> Settings:
    return Settings(base_url=BASE_URL)


@pytest.mark.parametrize("status", [200, 201])
def test_success_status_passes(
    mocked_responses: responses.RequestsMock, settings: Settings, status: int
) -> None:
    mocked_responses.get(PING_URL, status=status)

    check_health(settings)


def test_error_status_raises(
    mocked_responses: responses.RequestsMock, settings: Settings
) -> None:
    mocked_responses.get(PING_URL, status=503)

    with pytest.raises(RuntimeError, match="Status 503"):
        check_health(settings)


def test_connection_error_raises(
    mocked_responses: responses.RequestsMock, settings: Settings
) -> None:
    mocked_responses.get(PING_URL, body=requests.ConnectionError())

    with pytest.raises(RuntimeError, match="unreachable"):
        check_health(settings)
