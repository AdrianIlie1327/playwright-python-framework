"""Builders for dynamic test data (unique per run, so tests stay independent)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from faker import Faker

_fake = Faker()


@dataclass(frozen=True)
class CustomerInfo:
    first_name: str
    last_name: str
    postal_code: str


def customer_info() -> CustomerInfo:
    return CustomerInfo(
        first_name=_fake.first_name(),
        last_name=_fake.last_name(),
        postal_code=_fake.postcode(),
    )


def new_product_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": f"QA {_fake.word().title()} {_fake.random_int(1000, 9999)}",
        "description": _fake.sentence(),
        "price": float(_fake.random_int(1, 500)),
        "category": "qa-automation",
        "brand": _fake.company(),
    }
    payload.update(overrides)
    return payload
