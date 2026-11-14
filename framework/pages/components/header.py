"""Header shown on every authenticated page (cart icon + side menu)."""

from __future__ import annotations

import allure
from playwright.sync_api import Locator, Page


class Header:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.cart_link: Locator = page.get_by_test_id("shopping-cart-link")
        self.cart_badge: Locator = page.get_by_test_id("shopping-cart-badge")
        self.menu_button: Locator = page.get_by_role("button", name="Open Menu")
        self.logout_link: Locator = page.get_by_test_id("logout-sidebar-link")

    @allure.step("Open cart")
    def open_cart(self) -> None:
        self.cart_link.click()

    @allure.step("Log out")
    def logout(self) -> None:
        self.menu_button.click()
        self.logout_link.click()
