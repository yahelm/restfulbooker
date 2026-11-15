from datetime import date

from restfulbooker.domains.booking.models import Booking, BookingDates
from test_data.booking_factory import BookingFactory


def test_build_returns_valid_booking() -> None:
    booking = BookingFactory().build()

    assert Booking.model_validate(booking.model_dump()) == booking
    assert booking.bookingdates.checkout > booking.bookingdates.checkin


def test_builds_have_unique_firstname() -> None:
    factory = BookingFactory()

    assert factory.build().firstname != factory.build().firstname


def test_overrides_replace_defaults() -> None:
    dates = BookingDates(checkin=date(2030, 1, 1), checkout=date(2030, 1, 5))

    booking = BookingFactory().build(totalprice=0, bookingdates=dates)

    assert booking.totalprice == 0
    assert booking.bookingdates == dates
