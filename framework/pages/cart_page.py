from __future__ import annotations

import allure
from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage
from framework.pages.checkout_pages import CheckoutInfoPage


class CartPage(BasePage):
    path = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items: Locator = page.get_by_test_id("inventory-item")
        self.item_names: Locator = page.get_by_test_id("inventory-item-name")
        self.checkout_button: Locator = page.get_by_test_id("checkout")

    @property
    def ready_locator(self) -> Locator:
        return self.checkout_button

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    @allure.step("Proceed to checkout")
    def checkout(self) -> CheckoutInfoPage:
        self.checkout_button.click()
        return CheckoutInfoPage(self.page).should_be_loaded()
