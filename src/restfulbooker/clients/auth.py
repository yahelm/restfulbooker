from requests import PreparedRequest
from requests.auth import AuthBase


class TokenAuth(AuthBase):
    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Cookie"] = f"token={self.token}"
        return request
