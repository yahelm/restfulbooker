from typing import Any

import pytest

from restfulbooker.clients.auth import TokenAuth
from restfulbooker.domains.auth.api import AuthApi
from restfulbooker.domains.auth.models import Credentials, Token
from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import Booking, CreatedBooking


def test_valid_credentials_return_token(
    auth_api: AuthApi, credentials: Credentials
) -> None:
    response = auth_api.create_token(credentials.model_dump())

    assert response.status_code == 200, response.text
    token = Token.model_validate_json(response.text)
    assert token.token


def test_each_call_returns_new_token(
    auth_api: AuthApi, credentials: Credentials
) -> None:
    first = auth_api.create_token(credentials.model_dump())
    second = auth_api.create_token(credentials.model_dump())

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    first_token = Token.model_validate_json(first.text).token
    second_token = Token.model_validate_json(second.text).token
    assert first_token != second_token


def test_token_authorizes_partial_update(
    auth_api: AuthApi,
    booking_api: BookingApi,
    credentials: Credentials,
    created_booking: CreatedBooking,
) -> None:
    token_response = auth_api.create_token(credentials.model_dump())
    assert token_response.status_code == 200, token_response.text
    auth = TokenAuth(Token.model_validate_json(token_response.text).token)

    response = booking_api.partial_update_booking(
        created_booking.bookingid, {"firstname": "Token"}, auth=auth
    )

    assert response.status_code == 200, response.text
    assert Booking.model_validate_json(response.text).firstname == "Token"


def test_wrong_password_returns_401(
    auth_api: AuthApi, credentials: Credentials
) -> None:
    payload = {"username": credentials.username, "password": "wrong-password"}

    response = auth_api.create_token(payload)

    assert response.status_code == 401, response.text


def test_unknown_username_returns_401(
    auth_api: AuthApi, credentials: Credentials
) -> None:
    payload = {"username": "unknown-user", "password": credentials.password}

    response = auth_api.create_token(payload)

    assert response.status_code == 401, response.text


@pytest.mark.parametrize("missing_field", ["username", "password"])
def test_missing_field_returns_400(
    auth_api: AuthApi, credentials: Credentials, missing_field: str
) -> None:
    payload = credentials.model_dump()
    del payload[missing_field]

    response = auth_api.create_token(payload)

    assert response.status_code == 400, response.text


def test_empty_body_returns_400(auth_api: AuthApi) -> None:
    payload: dict[str, Any] = {}

    response = auth_api.create_token(payload)

    assert response.status_code == 400, response.text


def test_empty_credentials_are_rejected(auth_api: AuthApi) -> None:
    payload = {"username": "", "password": ""}

    response = auth_api.create_token(payload)

    assert response.status_code in {400, 401}, response.text
