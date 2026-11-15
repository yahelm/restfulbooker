from collections.abc import Callable

from requests.auth import HTTPBasicAuth

from restfulbooker.domains.booking.api import BookingApi
from restfulbooker.domains.booking.models import Booking, CreatedBooking


def test_existing_booking_is_returned(
    booking_api: BookingApi, created_booking: CreatedBooking
) -> None:
    response = booking_api.get_booking(created_booking.bookingid)

    assert response.status_code == 200, response.text
    assert Booking.model_validate_json(response.text) == created_booking.booking


def test_deleted_booking_returns_404(
    booking_api: BookingApi,
    booking_creator: Callable[..., CreatedBooking],
    basic_auth: HTTPBasicAuth,
) -> None:
    booking_id = booking_creator().bookingid
    deleted = booking_api.delete_booking(booking_id, auth=basic_auth)
    assert deleted.ok, deleted.text

    response = booking_api.get_booking(booking_id)

    assert response.status_code == 404, response.text


def test_non_numeric_id_returns_404(booking_api: BookingApi) -> None:
    response = booking_api.get_booking("abc")

    assert response.status_code == 404, response.text
