# restfulbooker

Pytest API test framework for the [Restful Booker](https://restful-booker.herokuapp.com/apidoc/index.html) sandbox API.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) — Python package and project manager
- Python 3.12

## Quick setup

**Install required tools:**

```shell
brew install uv
```

**Configure environment variables:**

```shell
cp .env.example .env
```

**Install dependencies:**

```shell
make py/install
```

**Run API tests:**

```shell
make test/api
```

The run starts with a health check (`GET /ping`). The JUnit report is written to `reports/junit.xml`.

**Run framework unit tests:**

```shell
make test/unit
```

**Run linters:**

```shell
make py/lint
```

Pass extra pytest arguments with `opts`, for example `make test/api opts="tests/api/booking"`.

## Test design

- Tests assert the correct HTTP behaviour (RFC 9110). Known defects stay red, with no `xfail`.
- Each test creates its own booking with a unique `firstname`. A fixture teardown deletes it.
- PUT, PATCH and DELETE are tested with both token and Basic auth.

## Known defects

| Defect | Expected | Actual | Tests |
| --- | --- | --- | --- |
| `GET /ping` status | 200 | 201 | `test_ping.py` |
| `POST /auth` accepts bad or missing credentials | 400 / 401 | 200 | `test_auth.py` |
| `POST /booking` success status | 201 | 200 | `test_create_booking.py` |
| `POST /booking` with a missing field | 400 | 500 | `test_create_booking.py` |
| `POST`, `PUT`, `PATCH` accept invalid data | 400 | 200 | `test_create_booking.py`, `test_update_booking.py`, `test_partial_update_booking.py` |
| Missing or invalid auth | 401 | 403 | `test_update_booking.py`, `test_partial_update_booking.py`, `test_delete_booking.py` |
| Booking that does not exist | 404 | 405 | `test_update_booking.py`, `test_partial_update_booking.py`, `test_delete_booking.py` |
| `DELETE /booking/:id` success status | 200 / 204 | 201 | `test_delete_booking.py` |
| `checkin` / `checkout` filters do not match the docs | — | — | `test_list_bookings.py` |
| `GET /booking` with an invalid date | 400 | 500 | `test_list_bookings.py` |
