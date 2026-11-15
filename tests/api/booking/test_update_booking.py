from collections.abc import Callable
from typing import Any

import pytest
from requests.auth import AuthBase, HTTPBasicAuth

from restfulbooker.clients.auth import TokenAuth
from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import Booking, CreatedBooking
from test_data.booking_factory import BookingFactory


def to_payload(booking: Booking) -> dict[str, Any]:
    return booking.model_dump(mode="json", exclude_none=True)


@pytest.mark.parametrize("auth_fixture", ["token_auth", "basic_auth"])
def test_full_update_returns_new_booking(
    request: pytest.FixtureRequest,
    auth_fixture: str,
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    created_booking: CreatedBooking,
) -> None:
    auth: AuthBase = request.getfixturevalue(auth_fixture)
    new_booking = booking_factory.build()

    response = booking_api.update_booking(
        created_booking.bookingid, to_payload(new_booking), auth=auth
    )

    assert response.status_code == 200, response.text
    assert Booking.model_validate_json(response.text) == new_booking


def test_full_update_is_stored(
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    new_booking = booking_factory.build()
    updated = booking_api.update_booking(
        created_booking.bookingid, to_payload(new_booking), auth=basic_auth
    )
    assert updated.ok, updated.text

    response = booking_api.get_booking(created_booking.bookingid)

    assert response.status_code == 200, response.text
    assert Booking.model_validate_json(response.text) == new_booking


def test_update_without_auth_returns_401(
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    created_booking: CreatedBooking,
) -> None:
    payload = to_payload(booking_factory.build())

    response = booking_api.update_booking(created_booking.bookingid, payload)

    assert response.status_code == 401, response.text


@pytest.mark.parametrize(
    "auth",
    [TokenAuth("invalid-token"), HTTPBasicAuth("admin", "wrong-password")],
    ids=["invalid_token", "invalid_basic"],
)
def test_update_with_invalid_auth_returns_401(
    auth: AuthBase,
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    created_booking: CreatedBooking,
) -> None:
    payload = to_payload(booking_factory.build())

    response = booking_api.update_booking(created_booking.bookingid, payload, auth=auth)

    assert response.status_code == 401, response.text


def test_update_without_required_field_returns_400(
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    payload = to_payload(booking_factory.build())
    del payload["firstname"]

    response = booking_api.update_booking(
        created_booking.bookingid, payload, auth=basic_auth
    )

    assert response.status_code == 400, response.text


def test_update_with_wrong_type_returns_400(
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    payload = to_payload(booking_factory.build())
    payload["totalprice"] = "abc"

    response = booking_api.update_booking(
        created_booking.bookingid, payload, auth=basic_auth
    )

    assert response.status_code == 400, response.text


def test_update_deleted_booking_returns_404(
    booking_api: BookingApi,
    booking_factory: BookingFactory,
    booking_creator: Callable[..., CreatedBooking],
    basic_auth: HTTPBasicAuth,
) -> None:
    booking_id = booking_creator().bookingid
    deleted = booking_api.delete_booking(booking_id, auth=basic_auth)
    assert deleted.ok, deleted.text
    payload = to_payload(booking_factory.build())

    response = booking_api.update_booking(booking_id, payload, auth=basic_auth)

    assert response.status_code == 404, response.text
