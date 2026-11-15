from datetime import date, timedelta
from typing import Any
from uuid import uuid4

from faker import Faker

from restfulbooker.domains.booking.models import Booking, BookingDates
from test_data.factory import BaseFactory

fake = Faker()


class BookingFactory(BaseFactory[Booking]):
    model = Booking

    def defaults(self) -> dict[str, Any]:
        checkin = date.today() + timedelta(days=fake.random_int(min=1, max=365))
        checkout = checkin + timedelta(days=fake.random_int(min=1, max=14))
        return {
            "firstname": f"{fake.first_name()}-{uuid4().hex[:8]}",
            "lastname": fake.last_name(),
            "totalprice": fake.random_int(min=50, max=1000),
            "depositpaid": fake.boolean(),
            "bookingdates": BookingDates(checkin=checkin, checkout=checkout),
            "additionalneeds": fake.random_element(["Breakfast", "Lunch", "Parking"]),
        }
