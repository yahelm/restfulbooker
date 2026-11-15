import pytest

from restfulbooker.clients.healthcheck import check_health
from restfulbooker.config import Settings


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--skip-healthcheck",
        action="store_true",
        help="Skip real API check before test run",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    config = session.config
    if config.getoption("--skip-healthcheck"):
        return
    try:
        check_health(Settings())
    except RuntimeError as error:
        pytest.exit(f"Healthcheck failed with: {error}", returncode=1)
