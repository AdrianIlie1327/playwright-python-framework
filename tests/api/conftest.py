"""API fixtures built on Playwright's APIRequestContext (no browser is launched).

Note: an APIRequestContext keeps cookies like a browser does. The session-scoped context is
shared (and becomes authenticated once anything logs in), so tests that need a clean,
anonymous client must use ``anonymous_auth_client``.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from framework.api import AuthClient, ProductsClient
from framework.config import Settings


def _new_api_context(playwright: Playwright, settings: Settings) -> APIRequestContext:
    return playwright.request.new_context(
        base_url=settings.api.base_url,
        extra_http_headers={"Accept": "application/json"},
        timeout=settings.timeouts.default_ms,
    )


@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright, settings: Settings
) -> Generator[APIRequestContext, None, None]:
    context = _new_api_context(playwright, settings)
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def auth_client(api_request_context: APIRequestContext) -> AuthClient:
    return AuthClient(api_request_context)


@pytest.fixture
def anonymous_auth_client(
    playwright: Playwright, settings: Settings
) -> Generator[AuthClient, None, None]:
    """Auth client on a fresh context: no cookies or tokens from other tests."""
    context = _new_api_context(playwright, settings)
    yield AuthClient(context)
    context.dispose()


@pytest.fixture(scope="session")
def products_client(api_request_context: APIRequestContext) -> ProductsClient:
    return ProductsClient(api_request_context)


@pytest.fixture(scope="session")
def access_token(auth_client: AuthClient, settings: Settings) -> str:
    """One login per session (per worker under xdist)."""
    return auth_client.get_access_token(
        settings.api.username, settings.api.password.get_secret_value()
    )
