from collections.abc import Callable
from datetime import timedelta
from typing import Any

import pytest
import requests

from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import Booking, BookingDates, CreatedBooking
from test_data.booking_factory import BookingFactory

PostBooking = Callable[[dict[str, Any]], requests.Response]


@pytest.fixture
def post_booking(booking_api: BookingApi, booking_cleanup: list[int]) -> PostBooking:

    def post(payload: dict[str, Any]) -> requests.Response:
        response = booking_api.create_booking(payload)
        if response.ok:
            booking_cleanup.append(response.json()["bookingid"])
        return response

    return post


def to_payload(booking: Booking) -> dict[str, Any]:
    return booking.model_dump(mode="json", exclude_none=True)


def test_valid_booking_returns_201(
    post_booking: PostBooking, booking_factory: BookingFactory
) -> None:
    payload = to_payload(booking_factory.build())

    response = post_booking(payload)

    assert response.status_code == 201, response.text


def test_response_contains_created_booking(
    post_booking: PostBooking, booking_factory: BookingFactory
) -> None:
    booking = booking_factory.build()

    response = post_booking(to_payload(booking))

    assert response.ok, response.text
    created = CreatedBooking.model_validate_json(response.text)
    assert created.bookingid > 0
    assert created.booking == booking


def test_created_booking_is_stored(
    post_booking: PostBooking,
    booking_api: BookingApi,
    booking_factory: BookingFactory,
) -> None:
    booking = booking_factory.build()
    response = post_booking(to_payload(booking))
    assert response.ok, response.text
    booking_id = CreatedBooking.model_validate_json(response.text).bookingid

    stored = booking_api.get_booking(booking_id)

    assert stored.status_code == 200, stored.text
    assert Booking.model_validate_json(stored.text) == booking


def test_booking_without_additionalneeds_returns_201(
    post_booking: PostBooking, booking_factory: BookingFactory
) -> None:
    payload = to_payload(booking_factory.build(additionalneeds=None))

    response = post_booking(payload)

    assert response.status_code == 201, response.text


@pytest.mark.parametrize(
    "missing_field",
    ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
)
def test_missing_field_returns_400(
    post_booking: PostBooking, booking_factory: BookingFactory, missing_field: str
) -> None:
    payload = to_payload(booking_factory.build())
    del payload[missing_field]

    response = post_booking(payload)

    assert response.status_code == 400, response.text


@pytest.mark.parametrize(
    ("field", "value"),
    [("totalprice", "abc"), ("depositpaid", "yes")],
)
def test_wrong_type_returns_400(
    post_booking: PostBooking,
    booking_factory: BookingFactory,
    field: str,
    value: str,
) -> None:
    payload = to_payload(booking_factory.build())
    payload[field] = value

    response = post_booking(payload)

    assert response.status_code == 400, response.text


def test_invalid_date_returns_400(
    post_booking: PostBooking, booking_factory: BookingFactory
) -> None:
    payload = to_payload(booking_factory.build())
    payload["bookingdates"]["checkin"] = "2026-13-45"

    response = post_booking(payload)

    assert response.status_code == 400, response.text


def test_checkout_before_checkin_returns_400(
    post_booking: PostBooking, booking_factory: BookingFactory
) -> None:
    dates = booking_factory.build().bookingdates
    reversed_dates = BookingDates(
        checkin=dates.checkin, checkout=dates.checkin - timedelta(days=1)
    )
    payload = to_payload(booking_factory.build(bookingdates=reversed_dates))

    response = post_booking(payload)

    assert response.status_code == 400, response.text


def test_zero_totalprice_returns_201(
    post_booking: PostBooking, booking_factory: BookingFactory
) -> None:
    payload = to_payload(booking_factory.build(totalprice=0))

    response = post_booking(payload)

    assert response.status_code == 201, response.text


def test_negative_totalprice_returns_400(
    post_booking: PostBooking, booking_factory: BookingFactory
) -> None:
    payload = to_payload(booking_factory.build(totalprice=-1))

    response = post_booking(payload)

    assert response.status_code == 400, response.text
