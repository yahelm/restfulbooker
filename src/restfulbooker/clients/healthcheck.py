import requests

from restfulbooker.clients.rest_client import RestClient
from restfulbooker.config import Settings


def check_health(settings: Settings) -> None:
    client = RestClient(str(settings.base_url), settings.healthcheck_timeout)
    try:
        response = client.get("/ping")
    except requests.RequestException as error:
        raise RuntimeError("Endpoint is unreachable") from error

    if not response.ok:
        raise RuntimeError(f"Healthcheck GET /ping: Status {response.status_code}")
