from __future__ import annotations

from typing import Any

from playwright.sync_api import APIResponse

from framework.api.base_client import BaseClient


class ProductsClient(BaseClient):
    BASE = "/products"

    def list_products(self, limit: int | None = None, skip: int | None = None) -> APIResponse:
        params = {k: v for k, v in {"limit": limit, "skip": skip}.items() if v is not None}
        return self.get(self.BASE, params=params)

    def get_by_id(self, product_id: int) -> APIResponse:
        return self.get(f"{self.BASE}/{product_id}")

    def search(self, query: str) -> APIResponse:
        return self.get(f"{self.BASE}/search", params={"q": query})

    def create(self, payload: dict[str, Any]) -> APIResponse:
        return self.post(f"{self.BASE}/add", data=payload)

    def update(self, product_id: int, payload: dict[str, Any]) -> APIResponse:
        return self.put(f"{self.BASE}/{product_id}", data=payload)

    def remove(self, product_id: int) -> APIResponse:
        return self.delete(f"{self.BASE}/{product_id}")
