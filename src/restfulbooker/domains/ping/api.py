import requests

from restfulbooker.clients.rest_client import RestClient


class PingApi:
    def __init__(self, client: RestClient) -> None:
        self.client = client

    def ping(self) -> requests.Response:
        return self.client.get("/ping")
