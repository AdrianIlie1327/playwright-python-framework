import allure
import pytest
from playwright.sync_api import expect

from framework.pages import InventoryPage
from framework.utils import data_factory
from framework.utils.test_data import load_json

PRODUCTS = load_json("ui.json")["products"]


@allure.epic("Web Shop")
@allure.feature("Checkout")
class TestCheckout:
    @pytest.mark.smoke
    @allure.title("Customer can buy several products end to end")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_end_to_end_purchase(self, inventory_page: InventoryPage) -> None:
        selected = [PRODUCTS["backpack"], PRODUCTS["bolt_tshirt"]]
        for name in selected:
            inventory_page.add_to_cart(name)

        cart = inventory_page.go_to_cart()
        assert sorted(cart.names()) == sorted(selected)

        overview = cart.checkout().continue_to_overview(data_factory.customer_info())

        with allure.step("Verify order totals"):
            assert overview.subtotal() == overview.item_prices_sum()
            assert overview.total() == pytest.approx(overview.subtotal() + overview.tax())

        complete = overview.finish()
        expect(complete.complete_header).to_have_text("Thank you for your order!")
        expect(inventory_page.header.cart_badge).to_be_hidden()

    @pytest.mark.regression
    @allure.title("Checkout requires customer information")
    def test_checkout_requires_info(self, inventory_page: InventoryPage) -> None:
        inventory_page.add_to_cart(PRODUCTS["backpack"])
        info_page = inventory_page.go_to_cart().checkout()

        info_page.continue_button.click()

        expect(info_page.error_message).to_contain_text("First Name is required")
