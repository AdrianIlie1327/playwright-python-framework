import allure
import pytest
from playwright.sync_api import expect

from framework.config import Settings
from framework.pages import LoginPage
from framework.utils.test_data import load_json

USERS = load_json("ui.json")["users"]


@allure.epic("Web Shop")
@allure.feature("Authentication")
class TestLogin:
    @pytest.mark.smoke
    @allure.title("User can log in with valid credentials")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_valid_login(self, login_page: LoginPage, settings: Settings) -> None:
        inventory = login_page.login(settings.ui.username, settings.ui.password.get_secret_value())

        expect(inventory.title).to_have_text("Products")
        expect(inventory.items).not_to_have_count(0)

    @pytest.mark.regression
    @allure.title("Login is rejected: {case}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        ("case", "expected_error"),
        [
            ("locked_out", "Sorry, this user has been locked out."),
            ("invalid_password", "Username and password do not match any user in this service"),
            ("unknown_user", "Username and password do not match any user in this service"),
        ],
    )
    def test_invalid_login(self, login_page: LoginPage, case: str, expected_error: str) -> None:
        user = USERS[case]

        login_page.submit(user["username"], user["password"])

        expect(login_page.error_message).to_contain_text(expected_error)
        login_page.should_be_loaded()

    @pytest.mark.regression
    @allure.title("Login requires a username")
    def test_empty_username(self, login_page: LoginPage) -> None:
        login_page.submit("", "any")

        expect(login_page.error_message).to_contain_text("Username is required")

    @pytest.mark.regression
    @allure.title("User can log out")
    def test_logout(self, login_page: LoginPage, settings: Settings) -> None:
        inventory = login_page.login(settings.ui.username, settings.ui.password.get_secret_value())

        inventory.header.logout()

        login_page.should_be_loaded()
