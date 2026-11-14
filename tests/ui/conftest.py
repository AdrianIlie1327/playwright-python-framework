"""UI fixtures. Browser selection (--browser, --headed, --slowmo, --device...) comes from
pytest-playwright; this file wires it to the active environment and the page objects."""

from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import Page, Playwright, expect

from framework.config import Settings
from framework.pages import InventoryPage, LoginPage


@pytest.fixture(scope="session", autouse=True)
def _configure_playwright(playwright: Playwright, settings: Settings) -> None:
    # The app under test marks elements with data-test="..." -> page.get_by_test_id("...")
    playwright.selectors.set_test_id_attribute("data-test")
    expect.set_options(timeout=settings.timeouts.expect_ms)


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """Overrides pytest-base-url so page.goto('/path') resolves against the active env."""
    return settings.ui.base_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "locale": "en-US",
        "timezone_id": "UTC",
    }


@pytest.fixture
def page(page: Page, settings: Settings) -> Page:
    page.set_default_timeout(settings.timeouts.default_ms)
    page.set_default_navigation_timeout(settings.timeouts.navigation_ms)
    return page


# ---------------------------------------------------------------------------
# Page objects
# ---------------------------------------------------------------------------
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page).open()


@pytest.fixture
def inventory_page(login_page: LoginPage, settings: Settings) -> InventoryPage:
    """Starts the test already logged in as the default user."""
    return login_page.login(settings.ui.username, settings.ui.password.get_secret_value())
