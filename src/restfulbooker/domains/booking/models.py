from datetime import date

from restfulbooker.domains.base import StrictModel


class BookingDates(StrictModel):
    checkin: date
    checkout: date


class Booking(StrictModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None


class CreatedBooking(StrictModel):
    bookingid: int
    booking: Booking


class BookingId(StrictModel):
    bookingid: int
