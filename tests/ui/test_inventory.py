import allure
import pytest
from playwright.sync_api import expect

from framework.pages import InventoryPage, SortOption
from framework.utils.test_data import load_json

PRODUCTS = load_json("ui.json")["products"]


@allure.epic("Web Shop")
@allure.feature("Product catalogue")
class TestInventory:
    @pytest.mark.regression
    @allure.story("Sorting")
    @allure.title("Products can be sorted by {option.name}")
    @pytest.mark.parametrize(
        "option", [SortOption.NAME_ASC, SortOption.NAME_DESC], ids=lambda o: o.name
    )
    def test_sort_by_name(self, inventory_page: InventoryPage, option: SortOption) -> None:
        inventory_page.sort_by(option)

        names = inventory_page.names()
        assert names == sorted(names, reverse=option is SortOption.NAME_DESC)

    @pytest.mark.regression
    @allure.story("Sorting")
    @allure.title("Products can be sorted by {option.name}")
    @pytest.mark.parametrize(
        "option", [SortOption.PRICE_ASC, SortOption.PRICE_DESC], ids=lambda o: o.name
    )
    def test_sort_by_price(self, inventory_page: InventoryPage, option: SortOption) -> None:
        inventory_page.sort_by(option)

        prices = inventory_page.prices()
        assert prices == sorted(prices, reverse=option is SortOption.PRICE_DESC)

    @pytest.mark.smoke
    @allure.story("Cart")
    @allure.title("Adding and removing products updates the cart badge")
    def test_cart_badge(self, inventory_page: InventoryPage) -> None:
        badge = inventory_page.header.cart_badge

        inventory_page.add_to_cart(PRODUCTS["backpack"])
        inventory_page.add_to_cart(PRODUCTS["bike_light"])
        expect(badge).to_have_text("2")

        inventory_page.remove_from_cart(PRODUCTS["backpack"])
        expect(badge).to_have_text("1")

        inventory_page.remove_from_cart(PRODUCTS["bike_light"])
        expect(badge).to_be_hidden()
