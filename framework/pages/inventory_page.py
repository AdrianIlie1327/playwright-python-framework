from __future__ import annotations

from enum import StrEnum

import allure
from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage
from framework.pages.cart_page import CartPage
from framework.pages.components import Header


class SortOption(StrEnum):
    NAME_ASC = "az"
    NAME_DESC = "za"
    PRICE_ASC = "lohi"
    PRICE_DESC = "hilo"


class InventoryPage(BasePage):
    path = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.title: Locator = page.get_by_test_id("title")
        self.items: Locator = page.get_by_test_id("inventory-item")
        self.item_names: Locator = page.get_by_test_id("inventory-item-name")
        self.item_prices: Locator = page.get_by_test_id("inventory-item-price")
        self.sort_select: Locator = page.get_by_test_id("product-sort-container")

    @property
    def ready_locator(self) -> Locator:
        return self.items.first

    def item(self, name: str) -> Locator:
        return self.items.filter(has=self.page.get_by_text(name, exact=True))

    @allure.step("Add {name} to cart")
    def add_to_cart(self, name: str) -> None:
        self.item(name).get_by_role("button", name="Add to cart").click()

    @allure.step("Remove {name} from cart")
    def remove_from_cart(self, name: str) -> None:
        self.item(name).get_by_role("button", name="Remove").click()

    @allure.step("Sort products by {option}")
    def sort_by(self, option: SortOption) -> None:
        self.sort_select.select_option(option.value)

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def prices(self) -> list[float]:
        return [float(p.lstrip("$")) for p in self.item_prices.all_inner_texts()]

    def go_to_cart(self) -> CartPage:
        self.header.open_cart()
        return CartPage(self.page).should_be_loaded()
