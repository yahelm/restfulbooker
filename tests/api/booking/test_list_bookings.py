from datetime import timedelta
from uuid import uuid4

import requests
from pydantic import TypeAdapter

from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import BookingId, CreatedBooking

BOOKING_IDS = TypeAdapter(list[BookingId])


def booking_ids(response: requests.Response) -> list[int]:
    return [item.bookingid for item in BOOKING_IDS.validate_json(response.text)]


def test_list_without_filters_contains_booking(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    response = booking_api.get_bookings()

    assert response.status_code == 200, response.text
    assert created_booking.bookingid in booking_ids(response)


def test_filter_by_firstname(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    response = booking_api.get_bookings(firstname=created_booking.booking.firstname)

    assert response.status_code == 200, response.text
    assert booking_ids(response) == [created_booking.bookingid]


def test_filter_by_firstname_and_lastname(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    booking = created_booking.booking

    response = booking_api.get_bookings(
        firstname=booking.firstname, lastname=booking.lastname
    )

    assert response.status_code == 200, response.text
    assert booking_ids(response) == [created_booking.bookingid]


def test_checkin_filter_includes_same_date(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    booking = created_booking.booking
    checkin = booking.bookingdates.checkin

    response = booking_api.get_bookings(
        firstname=booking.firstname, checkin=checkin.isoformat()
    )

    assert response.status_code == 200, response.text
    assert booking_ids(response) == [created_booking.bookingid]


def test_checkin_filter_excludes_earlier_booking(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    booking = created_booking.booking
    checkin = booking.bookingdates.checkin + timedelta(days=1)

    response = booking_api.get_bookings(
        firstname=booking.firstname, checkin=checkin.isoformat()
    )

    assert response.status_code == 200, response.text
    assert booking_ids(response) == []


def test_checkout_filter_includes_same_date(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    booking = created_booking.booking
    checkout = booking.bookingdates.checkout

    response = booking_api.get_bookings(
        firstname=booking.firstname, checkout=checkout.isoformat()
    )

    assert response.status_code == 200, response.text
    assert booking_ids(response) == [created_booking.bookingid]


def test_checkout_filter_excludes_earlier_booking(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    booking = created_booking.booking
    checkout = booking.bookingdates.checkout + timedelta(days=1)

    response = booking_api.get_bookings(
        firstname=booking.firstname, checkout=checkout.isoformat()
    )

    assert response.status_code == 200, response.text
    assert booking_ids(response) == []


def test_filter_without_match_returns_empty_list(booking_api: BookingApi) -> None:
    response = booking_api.get_bookings(firstname=f"no-match-{uuid4().hex}")

    assert response.status_code == 200, response.text
    assert booking_ids(response) == []


def test_invalid_date_filter_returns_400(booking_api: BookingApi) -> None:
    response = booking_api.get_bookings(checkin="not-a-date")

    assert response.status_code == 400, response.text
