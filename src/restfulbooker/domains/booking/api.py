from typing import Any

import requests
from requests.auth import AuthBase

from restfulbooker.clients.rest_client import RestClient


class BookingApi:
    PATH = "/booking"

    def __init__(self, client: RestClient) -> None:
        self.client = client

    def get_bookings(
        self,
        firstname: str | None = None,
        lastname: str | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
    ) -> requests.Response:
        filters = {
            "firstname": firstname,
            "lastname": lastname,
            "checkin": checkin,
            "checkout": checkout,
        }
        params = {name: value for name, value in filters.items() if value is not None}
        return self.client.get(self.PATH, params=params)

    def get_booking(self, booking_id: int | str) -> requests.Response:
        return self.client.get(f"{self.PATH}/{booking_id}")

    def create_booking(self, payload: dict[str, Any]) -> requests.Response:
        return self.client.post(self.PATH, json=payload)

    def update_booking(
        self,
        booking_id: int,
        payload: dict[str, Any],
        auth: AuthBase | None = None,
    ) -> requests.Response:
        return self.client.put(f"{self.PATH}/{booking_id}", json=payload, auth=auth)

    def partial_update_booking(
        self,
        booking_id: int,
        payload: dict[str, Any],
        auth: AuthBase | None = None,
    ) -> requests.Response:
        return self.client.patch(f"{self.PATH}/{booking_id}", json=payload, auth=auth)

    def delete_booking(
        self, booking_id: int, auth: AuthBase | None = None
    ) -> requests.Response:
        return self.client.delete(f"{self.PATH}/{booking_id}", auth=auth)
