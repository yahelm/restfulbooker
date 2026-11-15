import pytest
from pydantic import ValidationError

from restfulbooker.domains.booking.models import Booking

VALID_JSON = (
    '{"firstname": "Jim", "lastname": "Brown", "totalprice": 111,'
    ' "depositpaid": true,'
    ' "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},'
    ' "additionalneeds": "Breakfast"}'
)


def test_valid_json_parses() -> None:
    booking = Booking.model_validate_json(VALID_JSON)

    assert booking.totalprice == 111


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('"totalprice": 111', '"totalprice": "111"'),
        ('"firstname": "Jim", ', ""),
        ('"firstname": "Jim"', '"firstname": "Jim", "extra": 1'),
    ],
    ids=["wrong_type", "missing_field", "extra_field"],
)
def test_invalid_json_raises(old: str, new: str) -> None:
    invalid_json = VALID_JSON.replace(old, new)

    with pytest.raises(ValidationError):
        Booking.model_validate_json(invalid_json)
