"""Thin wrapper over Playwright's APIRequestContext.

Every call runs inside an Allure step with the request and response attached, and is logged,
so a failed API test can be diagnosed straight from the report.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import allure
from playwright.sync_api import APIRequestContext, APIResponse

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, request: APIRequestContext) -> None:
        self._request = request

    def get(self, path: str, **kwargs: Any) -> APIResponse:
        return self._send("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> APIResponse:
        return self._send("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> APIResponse:
        return self._send("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> APIResponse:
        return self._send("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> APIResponse:
        return self._send("DELETE", path, **kwargs)

    def _send(self, method: str, path: str, **kwargs: Any) -> APIResponse:
        with allure.step(f"{method} {path}"):
            sent = {k: kwargs[k] for k in ("params", "data", "form") if kwargs.get(k)}
            if sent:
                allure.attach(
                    _to_json(sent), name="request", attachment_type=allure.attachment_type.JSON
                )

            response = self._request.fetch(path, method=method, **kwargs)

            logger.info("%s %s -> %s", method, response.url, response.status)
            allure.attach(
                f"{response.status} {response.status_text}\n{response.url}\n\n{_body(response)}",
                name=f"response {response.status}",
                attachment_type=allure.attachment_type.TEXT,
            )
            return response


def _to_json(value: Any) -> str:
    return json.dumps(value, indent=2, default=str)


def _body(response: APIResponse) -> str:
    try:
        return _to_json(response.json())
    except Exception:
        return response.text()
