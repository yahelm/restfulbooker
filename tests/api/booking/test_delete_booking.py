import pytest
from pydantic import TypeAdapter
from requests.auth import AuthBase, HTTPBasicAuth

from restfulbooker.clients.auth import TokenAuth
from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import BookingId, CreatedBooking

BOOKING_IDS = TypeAdapter(list[BookingId])


@pytest.mark.parametrize("auth_fixture", ["token_auth", "basic_auth"])
def test_delete_returns_success(
    request: pytest.FixtureRequest,
    auth_fixture: str,
    booking_api: BookingApi,
    created_booking: CreatedBooking,
) -> None:
    auth: AuthBase = request.getfixturevalue(auth_fixture)

    response = booking_api.delete_booking(created_booking.bookingid, auth=auth)

    assert response.status_code in {200, 204}, response.text


def test_deleted_booking_is_not_found(
    booking_api: BookingApi,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    deleted = booking_api.delete_booking(created_booking.bookingid, auth=basic_auth)
    assert deleted.ok, deleted.text

    response = booking_api.get_booking(created_booking.bookingid)

    assert response.status_code == 404, response.text


def test_deleted_booking_is_not_listed(
    booking_api: BookingApi,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    deleted = booking_api.delete_booking(created_booking.bookingid, auth=basic_auth)
    assert deleted.ok, deleted.text

    response = booking_api.get_bookings(firstname=created_booking.booking.firstname)

    assert response.status_code == 200, response.text
    assert BOOKING_IDS.validate_json(response.text) == []


def test_delete_without_auth_returns_401(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    response = booking_api.delete_booking(created_booking.bookingid)

    assert response.status_code == 401, response.text


@pytest.mark.parametrize(
    "auth",
    [TokenAuth("invalid-token"), HTTPBasicAuth("admin", "wrong-password")],
    ids=["invalid_token", "invalid_basic"],
)
def test_delete_with_invalid_auth_returns_401(
    auth: AuthBase,
    booking_api: BookingApi,
    created_booking: CreatedBooking,
) -> None:
    response = booking_api.delete_booking(created_booking.bookingid, auth=auth)

    assert response.status_code == 401, response.text


def test_failed_delete_keeps_booking(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    rejected = booking_api.delete_booking(created_booking.bookingid)
    assert not rejected.ok, rejected.text

    response = booking_api.get_booking(created_booking.bookingid)

    assert response.status_code == 200, response.text


def test_second_delete_returns_404(
    booking_api: BookingApi,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    first = booking_api.delete_booking(created_booking.bookingid, auth=basic_auth)
    assert first.ok, first.text

    response = booking_api.delete_booking(created_booking.bookingid, auth=basic_auth)

    assert response.status_code == 404, response.text
