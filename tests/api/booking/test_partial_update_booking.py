from collections.abc import Callable
from datetime import timedelta

import pytest
from requests.auth import AuthBase, HTTPBasicAuth

from restfulbooker.clients.auth import TokenAuth
from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import Booking, BookingDates, CreatedBooking


@pytest.mark.parametrize("auth_fixture", ["token_auth", "basic_auth"])
def test_partial_update_changes_field(
    request: pytest.FixtureRequest,
    auth_fixture: str,
    booking_api: BookingApi,
    created_booking: CreatedBooking,
) -> None:
    auth: AuthBase = request.getfixturevalue(auth_fixture)

    response = booking_api.partial_update_booking(
        created_booking.bookingid, {"firstname": "Patched"}, auth=auth
    )

    assert response.status_code == 200, response.text
    assert Booking.model_validate_json(response.text).firstname == "Patched"


def test_partial_update_keeps_other_fields(
    booking_api: BookingApi,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    patched = booking_api.partial_update_booking(
        created_booking.bookingid, {"firstname": "Patched"}, auth=basic_auth
    )
    assert patched.ok, patched.text
    expected = created_booking.booking.model_copy(update={"firstname": "Patched"})

    response = booking_api.get_booking(created_booking.bookingid)

    assert response.status_code == 200, response.text
    assert Booking.model_validate_json(response.text) == expected


def test_partial_update_of_nested_dates(
    booking_api: BookingApi,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    old_dates = created_booking.booking.bookingdates
    new_dates = BookingDates(
        checkin=old_dates.checkin + timedelta(days=1),
        checkout=old_dates.checkout + timedelta(days=1),
    )
    expected = created_booking.booking.model_copy(update={"bookingdates": new_dates})

    response = booking_api.partial_update_booking(
        created_booking.bookingid,
        {"bookingdates": new_dates.model_dump(mode="json")},
        auth=basic_auth,
    )

    assert response.status_code == 200, response.text
    assert Booking.model_validate_json(response.text) == expected


def test_partial_update_without_auth_returns_401(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    response = booking_api.partial_update_booking(
        created_booking.bookingid, {"firstname": "Patched"}
    )

    assert response.status_code == 401, response.text


@pytest.mark.parametrize(
    "auth",
    [TokenAuth("invalid-token"), HTTPBasicAuth("admin", "wrong-password")],
    ids=["invalid_token", "invalid_basic"],
)
def test_partial_update_with_invalid_auth_returns_401(
    auth: AuthBase,
    booking_api: BookingApi,
    created_booking: CreatedBooking,
) -> None:
    response = booking_api.partial_update_booking(
        created_booking.bookingid, {"firstname": "Patched"}, auth=auth
    )

    assert response.status_code == 401, response.text


def test_partial_update_with_wrong_type_returns_400(
    booking_api: BookingApi,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    response = booking_api.partial_update_booking(
        created_booking.bookingid, {"depositpaid": "yes"}, auth=basic_auth
    )

    assert response.status_code == 400, response.text


def test_partial_update_of_deleted_booking_returns_404(
    booking_api: BookingApi,
    booking_creator: Callable[..., CreatedBooking],
    basic_auth: HTTPBasicAuth,
) -> None:
    booking_id = booking_creator().bookingid
    deleted = booking_api.delete_booking(booking_id, auth=basic_auth)
    assert deleted.ok, deleted.text

    response = booking_api.partial_update_booking(
        booking_id, {"firstname": "Patched"}, auth=basic_auth
    )

    assert response.status_code == 404, response.text


def test_partial_update_with_checkout_before_checkin_returns_400(
    booking_api: BookingApi,
    created_booking: CreatedBooking,
    basic_auth: HTTPBasicAuth,
) -> None:
    checkin = created_booking.booking.bookingdates.checkin
    dates = {
        "checkin": checkin.isoformat(),
        "checkout": (checkin - timedelta(days=1)).isoformat(),
    }

    response = booking_api.partial_update_booking(
        created_booking.bookingid, {"bookingdates": dates}, auth=basic_auth
    )

    assert response.status_code == 400, response.text
