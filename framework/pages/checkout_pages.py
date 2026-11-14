"""The three steps of the checkout flow."""

from __future__ import annotations

import allure
from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage
from framework.utils.data_factory import CustomerInfo


class CheckoutInfoPage(BasePage):
    path = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name_input: Locator = page.get_by_test_id("firstName")
        self.last_name_input: Locator = page.get_by_test_id("lastName")
        self.postal_code_input: Locator = page.get_by_test_id("postalCode")
        self.continue_button: Locator = page.get_by_test_id("continue")
        self.error_message: Locator = page.get_by_test_id("error")

    @property
    def ready_locator(self) -> Locator:
        return self.continue_button

    @allure.step("Fill customer information")
    def fill(self, customer: CustomerInfo) -> None:
        self.first_name_input.fill(customer.first_name)
        self.last_name_input.fill(customer.last_name)
        self.postal_code_input.fill(customer.postal_code)

    def continue_to_overview(self, customer: CustomerInfo) -> CheckoutOverviewPage:
        self.fill(customer)
        self.continue_button.click()
        return CheckoutOverviewPage(self.page).should_be_loaded()


class CheckoutOverviewPage(BasePage):
    path = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.item_names: Locator = page.get_by_test_id("inventory-item-name")
        self.item_prices: Locator = page.get_by_test_id("inventory-item-price")
        self.subtotal_label: Locator = page.get_by_test_id("subtotal-label")
        self.tax_label: Locator = page.get_by_test_id("tax-label")
        self.total_label: Locator = page.get_by_test_id("total-label")
        self.finish_button: Locator = page.get_by_test_id("finish")

    @property
    def ready_locator(self) -> Locator:
        return self.finish_button

    def item_prices_sum(self) -> float:
        return round(sum(float(p.lstrip("$")) for p in self.item_prices.all_inner_texts()), 2)

    def subtotal(self) -> float:
        return _amount(self.subtotal_label)

    def tax(self) -> float:
        return _amount(self.tax_label)

    def total(self) -> float:
        return _amount(self.total_label)

    @allure.step("Finish order")
    def finish(self) -> CheckoutCompletePage:
        self.finish_button.click()
        return CheckoutCompletePage(self.page).should_be_loaded()


class CheckoutCompletePage(BasePage):
    path = "/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.complete_header: Locator = page.get_by_test_id("complete-header")
        self.back_home_button: Locator = page.get_by_test_id("back-to-products")

    @property
    def ready_locator(self) -> Locator:
        return self.complete_header


def _amount(label: Locator) -> float:
    """'Item total: $39.98' -> 39.98"""
    return float(label.inner_text().rsplit("$", 1)[-1])
