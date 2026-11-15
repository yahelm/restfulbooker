import logging
from collections.abc import Mapping
from typing import Any

import requests
from requests.auth import AuthBase

logger = logging.getLogger(__name__)


class RestClient:
    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url.strip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def request(
        self,
        method: str,
        path: str,
        json: Any = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, Any] | None = None,
        auth: AuthBase | None = None,
    ) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.request(
            method,
            url,
            json=json,
            params=params,
            headers=headers,
            auth=auth,
            timeout=self.timeout,
        )
        self._log(response)
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    @staticmethod
    def _log(response: requests.Response) -> None:
        elapsed_ms = response.elapsed.total_seconds() * 1000
        logger.info(
            f"{response.request.method} {response.request.url} -> "
            f"{response.status_code} in {elapsed_ms:.0f} ms"
        )
