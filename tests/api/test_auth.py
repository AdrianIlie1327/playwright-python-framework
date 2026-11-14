import allure
import pytest

from framework.api import AuthClient
from framework.api.models import AuthResponse, ErrorResponse, User
from framework.config import Settings


@allure.epic("Platform API")
@allure.feature("Authentication")
class TestAuth:
    @pytest.mark.smoke
    @allure.title("Login with valid credentials returns tokens")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, auth_client: AuthClient, settings: Settings) -> None:
        response = auth_client.login(
            settings.api.username, settings.api.password.get_secret_value()
        )

        assert response.status == 200
        body = AuthResponse.model_validate(response.json())
        assert body.username == settings.api.username
        assert body.access_token
        assert body.refresh_token

    @pytest.mark.regression
    @allure.title("Login with wrong password is rejected")
    def test_login_invalid_password(self, auth_client: AuthClient, settings: Settings) -> None:
        response = auth_client.login(settings.api.username, "definitely-wrong")

        assert response.status == 400
        assert ErrorResponse.model_validate(response.json()).message == "Invalid credentials"

    @pytest.mark.smoke
    @allure.title("Current user is returned for a valid token")
    def test_me_with_token(
        self, auth_client: AuthClient, access_token: str, settings: Settings
    ) -> None:
        response = auth_client.me(access_token)

        assert response.status == 200
        assert User.model_validate(response.json()).username == settings.api.username

    @pytest.mark.regression
    @allure.title("Protected endpoint requires a token")
    def test_me_without_token(self, anonymous_auth_client: AuthClient) -> None:
        response = anonymous_auth_client.me()

        assert response.status == 401
        assert ErrorResponse.model_validate(response.json()).message == "Access Token is required"
