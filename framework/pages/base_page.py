"""Base class for all page objects.

Page objects expose *intent* (``login``, ``add_to_cart``) and locators; assertions on business
outcomes stay in the tests. ``should_be_loaded`` is the one built-in check every page offers,
so navigation helpers can return a page that is guaranteed to be ready.
"""

from __future__ import annotations

import re
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect


class BasePage:
    #: Path relative to the UI base_url.
    path: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def ready_locator(self) -> Locator:
        """An element that is only visible once the page has rendered."""
        return self.page.locator("body")

    def open(self) -> Self:
        with allure.step(f"Open {type(self).__name__} ({self.path})"):
            self.page.goto(self.path)
        return self.should_be_loaded()

    def should_be_loaded(self) -> Self:
        expect(self.page).to_have_url(re.compile(re.escape(self.path) + r"(\?.*)?$"))
        expect(self.ready_locator).to_be_visible()
        return self
