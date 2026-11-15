from typing import Any

import requests

from restfulbooker.clients.rest_client import RestClient


class AuthApi:
    def __init__(self, client: RestClient) -> None:
        self.client = client

    def create_token(self, payload: dict[str, Any]) -> requests.Response:
        return self.client.post("/auth", json=payload)
