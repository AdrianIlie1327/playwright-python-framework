"""Environment-aware settings.

Non-secret values (URLs, timeouts) live in ``config/environments/<env>.yaml``.
Secrets (credentials) and ad-hoc overrides come from environment variables, which can be
provided by a local ``.env`` file or by CI secrets.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENVIRONMENTS_DIR = PROJECT_ROOT / "config" / "environments"

# Environment variable -> (section, key) in the settings tree.
_ENV_OVERRIDES: dict[str, tuple[str, str]] = {
    "UI_BASE_URL": ("ui", "base_url"),
    "UI_USERNAME": ("ui", "username"),
    "UI_PASSWORD": ("ui", "password"),
    "API_BASE_URL": ("api", "base_url"),
    "API_USERNAME": ("api", "username"),
    "API_PASSWORD": ("api", "password"),
}


class Credentials(BaseModel):
    username: str = ""
    password: SecretStr = SecretStr("")


class UiSettings(Credentials):
    base_url: str


class ApiSettings(Credentials):
    base_url: str


class Timeouts(BaseModel):
    default_ms: int = Field(default=15_000, gt=0)
    navigation_ms: int = Field(default=30_000, gt=0)
    expect_ms: int = Field(default=5_000, gt=0)


class Settings(BaseModel):
    env: str
    ui: UiSettings
    api: ApiSettings
    timeouts: Timeouts = Timeouts()


def available_environments() -> list[str]:
    return sorted(p.stem for p in ENVIRONMENTS_DIR.glob("*.yaml"))


@lru_cache
def load_settings(env: str) -> Settings:
    """Load settings for ``env``, applying environment-variable overrides."""
    load_dotenv(PROJECT_ROOT / ".env", override=False)

    path = ENVIRONMENTS_DIR / f"{env}.yaml"
    if not path.is_file():
        raise ValueError(
            f"Unknown environment '{env}'. Available: {', '.join(available_environments())}"
        )

    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for var, (section, key) in _ENV_OVERRIDES.items():
        if value := os.getenv(var):
            data.setdefault(section, {})[key] = value

    return Settings(env=env, **data)
