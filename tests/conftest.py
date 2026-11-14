"""Shared fixtures and hooks for every test suite."""

from __future__ import annotations

import os
import platform
import shutil
from collections.abc import Generator
from pathlib import Path

import allure
import pytest

from framework.config import PROJECT_ROOT, Settings, available_environments, load_settings

TESTS_DIR = Path(__file__).parent

# Playwright artifact kinds (from pytest-playwright's report.user_properties) -> Allure type.
_ARTIFACT_TYPES = {
    "playwright_screenshot": allure.attachment_type.PNG,
    "playwright_video": allure.attachment_type.WEBM,
    "playwright_trace": None,  # zip: attached as a raw file, open with `playwright show-trace`
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        default=os.getenv("TEST_ENV", "dev"),
        choices=available_environments(),
        help="Target environment (config/environments/<env>.yaml). Default: $TEST_ENV or dev.",
    )


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return load_settings(pytestconfig.getoption("--env"))


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Tag tests with their suite marker based on their folder (tests/ui -> ui, ...)."""
    for item in items:
        suite = item.path.relative_to(TESTS_DIR).parts[0]
        if suite in ("ui", "api"):
            item.add_marker(suite)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield
    # pytest-playwright (trylast, so it ran before this point) lists the artifacts it kept for
    # a failing test on the teardown report; mirror them into the Allure result.
    if report.when == "teardown":
        for kind, path in report.user_properties:
            if kind in _ARTIFACT_TYPES and Path(path).is_file():
                allure.attach.file(
                    path,
                    name=f"{kind.removeprefix('playwright_')}: {Path(path).name}",
                    attachment_type=_ARTIFACT_TYPES[kind],
                    extension=None if _ARTIFACT_TYPES[kind] else "zip",
                )
    return report


def pytest_html_report_title(report) -> None:  # type: ignore[no-untyped-def]
    report.title = "Test Automation Report"


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Write Allure environment + failure categories (controller process only under xdist)."""
    config = session.config
    if hasattr(config, "workerinput"):
        return
    allure_dir = config.getoption("allure_report_dir", default=None)
    if not allure_dir:
        return

    results = Path(allure_dir)
    results.mkdir(parents=True, exist_ok=True)
    settings = load_settings(config.getoption("--env"))
    browsers = config.getoption("browser", default=None) or ["chromium"]
    env_props = {
        "Environment": settings.env,
        "UI.Base.URL": settings.ui.base_url,
        "API.Base.URL": settings.api.base_url,
        "Browsers": ", ".join(browsers),
        "Headed": config.getoption("headed", default=False),
        "Python": platform.python_version(),
        "OS": platform.platform(terse=True),
    }
    (results / "environment.properties").write_text(
        "\n".join(f"{k}={v}" for k, v in env_props.items()), encoding="utf-8"
    )

    categories = PROJECT_ROOT / "config" / "allure" / "categories.json"
    if categories.is_file():
        shutil.copyfile(categories, results / "categories.json")
