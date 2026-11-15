from collections.abc import Callable, Iterator
from typing import Any

import pytest
from requests.auth import HTTPBasicAuth

from restfulbooker.clients.auth import TokenAuth
from restfulbooker.clients.rest_client import RestClient
from restfulbooker.config import Settings
from restfulbooker.domains.auth.api import AuthApi
from restfulbooker.domains.auth.models import Credentials, Token
from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import CreatedBooking
from restfulbooker.domains.ping.api import PingApi
from test_data.booking_factory import BookingFactory


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def client(settings: Settings) -> RestClient:
    return RestClient(str(settings.base_url), settings.request_timeout)


@pytest.fixture(scope="session")
def ping_api(client: RestClient) -> PingApi:
    return PingApi(client)


@pytest.fixture(scope="session")
def auth_api(client: RestClient) -> AuthApi:
    return AuthApi(client)


@pytest.fixture(scope="session")
def booking_api(client: RestClient) -> BookingApi:
    return BookingApi(client)


@pytest.fixture(scope="session")
def credentials(settings: Settings) -> Credentials:
    return Credentials(username=settings.username, password=settings.password)


@pytest.fixture(scope="session")
def basic_auth(credentials: Credentials) -> HTTPBasicAuth:
    return HTTPBasicAuth(credentials.username, credentials.password)


@pytest.fixture(scope="session")
def token_auth(auth_api: AuthApi, credentials: Credentials) -> TokenAuth:
    response = auth_api.create_token(credentials.model_dump())
    if not response.ok:
        raise RuntimeError(f"Setup: POST /auth -> {response.status_code}")
    return TokenAuth(Token.model_validate_json(response.text).token)


@pytest.fixture
def booking_factory() -> BookingFactory:
    return BookingFactory()


@pytest.fixture
def booking_cleanup(
    booking_api: BookingApi, basic_auth: HTTPBasicAuth
) -> Iterator[list[int]]:
    booking_ids: list[int] = []

    yield booking_ids

    for booking_id in booking_ids:
        booking_api.delete_booking(booking_id, auth=basic_auth)


@pytest.fixture
def booking_creator(
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    booking_cleanup: list[int],
) -> Callable[..., CreatedBooking]:

    def create(**overrides: Any) -> CreatedBooking:
        booking = booking_factory.build(**overrides)
        response = booking_api.create_booking(
            booking.model_dump(mode="json", exclude_none=True)
        )
        if not response.ok:
            raise RuntimeError(f"Setup: POST /booking -> {response.status_code}")
        created = CreatedBooking.model_validate_json(response.text)
        booking_cleanup.append(created.bookingid)
        return created

    return create


@pytest.fixture
def created_booking(
    booking_creator: Callable[..., CreatedBooking],
) -> CreatedBooking:
    return booking_creator()
