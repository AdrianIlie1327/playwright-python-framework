from __future__ import annotations

import allure
from playwright.sync_api import APIResponse

from framework.api.base_client import BaseClient
from framework.api.models import AuthResponse


class AuthClient(BaseClient):
    def login(self, username: str, password: str, expires_in_mins: int = 30) -> APIResponse:
        return self.post(
            "/auth/login",
            data={"username": username, "password": password, "expiresInMins": expires_in_mins},
        )

    @allure.step("Obtain access token for {username}")
    def get_access_token(self, username: str, password: str) -> str:
        response = self.login(username, password)
        assert response.ok, f"Login failed: {response.status} {response.text()}"
        return AuthResponse.model_validate(response.json()).access_token

    def me(self, token: str | None = None) -> APIResponse:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        return self.get("/auth/me", headers=headers)
