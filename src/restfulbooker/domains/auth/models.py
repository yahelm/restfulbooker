from restfulbooker.domains.base import StrictModel


class Credentials(StrictModel):
    username: str
    password: str


class Token(StrictModel):
    token: str
