from restfulbooker.domains.ping.api import PingApi


def test_ping_returns_200(ping_api: PingApi) -> None:
    response = ping_api.ping()

    assert response.status_code == 201, response.text
