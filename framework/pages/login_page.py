from __future__ import annotations

import allure
from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage
from framework.pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input: Locator = page.get_by_test_id("username")
        self.password_input: Locator = page.get_by_test_id("password")
        self.login_button: Locator = page.get_by_test_id("login-button")
        self.error_message: Locator = page.get_by_test_id("error")

    @property
    def ready_locator(self) -> Locator:
        return self.login_button

    @allure.step("Submit login form as {username}")
    def submit(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def login(self, username: str, password: str) -> InventoryPage:
        """Log in with valid credentials and return the loaded inventory page."""
        self.submit(username, password)
        return InventoryPage(self.page).should_be_loaded()
