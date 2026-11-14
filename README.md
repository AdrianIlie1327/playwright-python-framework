# Playwright Python Test Framework

[![Tests](https://github.com/AdrianIlie1327/playwright-python-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/AdrianIlie1327/playwright-python-framework/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/Allure-report-orange)](https://adrianilie1327.github.io/playwright-python-framework/)

UI and API test automation framework built with **Playwright**, **Pytest** and **Allure**, using the
Page Object Model, multi-environment configuration, cross-browser execution and GitHub Actions CI.

| Area | Tooling |
|---|---|
| UI automation | Playwright (sync API) via `pytest-playwright`: Chromium, Firefox, WebKit |
| API automation | Playwright `APIRequestContext` + Pydantic response models (contract checks) |
| Test runner | Pytest, `pytest-xdist` (parallel), `pytest-rerunfailures` (CI retries) |
| Reporting | Allure (steps, screenshots, videos, traces, history) and `pytest-html` |
| Config | Per-environment YAML + env vars / `.env` / CI secrets |
| Code quality | Ruff (lint + format), pre-commit, Dependabot |
| CI/CD | GitHub Actions: browser matrix, environment selection, Allure on GitHub Pages |

Demo targets: UI tests run against [SauceDemo](https://www.saucedemo.com), API tests against
[DummyJSON](https://dummyjson.com). Both are public sandboxes with published test credentials.

---

## Project structure

```
.
├── .github/
│   ├── workflows/tests.yml        # CI: lint → API + UI (browser matrix) → Allure report → Pages
│   └── dependabot.yml
├── config/
│   ├── environments/              # dev.yaml, staging.yaml, prod.yaml (URLs, timeouts; no secrets)
│   └── allure/categories.json     # failure classification in the Allure report
├── framework/
│   ├── config/settings.py         # typed settings loader (YAML + env var overrides)
│   ├── pages/                     # Page Object Model
│   │   ├── base_page.py           #   open(), should_be_loaded(), ready_locator
│   │   ├── components/header.py   #   reusable component shared by pages
│   │   └── login_page.py, inventory_page.py, cart_page.py, checkout_pages.py
│   ├── api/                       # API clients
│   │   ├── base_client.py         #   request wrapper: Allure steps, request/response attachments, logging
│   │   ├── auth_client.py, products_client.py
│   │   └── models.py              #   Pydantic response contracts
│   └── utils/                     # Faker data factory, static test data loader
├── test_data/                     # static test data (JSON)
├── tests/
│   ├── conftest.py                # --env option, settings, markers, Allure attachments/environment
│   ├── ui/                        # UI fixtures + tests
│   └── api/                       # API fixtures + tests
├── pyproject.toml                 # pytest + ruff configuration
├── requirements.txt               # pinned runtime deps
└── requirements-dev.txt           # + ruff, pre-commit
```

## Getting started

Prerequisites: Python 3.11+ (CI uses 3.12). [Allure CLI](https://allurereport.org/docs/install/) is optional
and only needed to view Allure reports locally (it requires Java).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install --with-deps        # or: playwright install chromium
cp .env.example .env                  # credentials for local runs
pre-commit install
```

## Running tests

```bash
pytest                                     # everything, default env (dev), Chromium, headless
pytest tests/api                           # API suite only
pytest tests/ui                            # UI suite only
pytest -m smoke                            # by marker: smoke | regression | ui | api
pytest -n auto                             # in parallel (pytest-xdist)
```

**Environment.** Use `--env` or the `TEST_ENV` variable. Values come from `config/environments/<env>.yaml`.

```bash
pytest --env staging
TEST_ENV=prod pytest -m smoke
```

**Browsers.** These options come from pytest-playwright.

```bash
pytest tests/ui --browser firefox
pytest tests/ui --browser chromium --browser firefox --browser webkit   # cross-browser run
pytest tests/ui --browser-channel chrome                                # branded Chrome / msedge
pytest tests/ui --headed --slowmo 300                                   # watch it run
pytest tests/ui --device "iPhone 15"                                    # mobile emulation
```

### Configuration precedence

1. `config/environments/<env>.yaml`: base URLs and timeouts per environment
2. Environment variables, which override the YAML: `UI_BASE_URL`, `UI_USERNAME`, `UI_PASSWORD`,
   `API_BASE_URL`, `API_USERNAME`, `API_PASSWORD`
3. A `.env` file (git-ignored) supplies those variables locally. In CI they come from GitHub
   **environment** variables and secrets (`dev`, `staging`, `prod`).

To add an environment, create `config/environments/<name>.yaml`. It becomes a valid `--env` choice
automatically. Add it to the workflow's `environment` options as well.

## Reports

Every run writes:

| Output | Path |
|---|---|
| Allure results | `reports/allure-results/` |
| HTML report (self-contained) | `reports/html/report.html` |
| Playwright trace / video / screenshot (failed tests only) | `reports/playwright/` |

```bash
allure serve reports/allure-results                      # build and open the Allure report
playwright show-trace reports/playwright/<test>/trace.zip
```

The Allure report includes:
- Epics, features, stories, severities and titles from test decorators
- Each API call as a step, with the request and response attached
- Page-object actions as steps
- Screenshot, video and Playwright trace attached to failed UI tests
- Environment info and failure categories (timeouts, locator changes, contract violations, etc.)
- Trend history across CI runs on GitHub Pages

## CI (GitHub Actions)

`.github/workflows/tests.yml` runs on push and PR to `main`, every weekday night, and on demand.

```
lint ──┬── API tests ─────────────────────┬── Allure report ──► GitHub Pages (main only)
       └── UI tests [chromium|firefox|webkit] ┘
```

- **Manual runs** (*Actions → Tests → Run workflow*) let you pick the environment, browser (or all),
  suite (`ui`/`api`/`all`) and a marker expression.
- Each job runs against a GitHub **Environment** (`dev`/`staging`/`prod`). Usernames are environment
  *variables* and passwords are environment *secrets*. You can add protection rules (e.g. required
  reviewers for `prod`).
- Tests run in parallel with up to 2 reruns for flaky infrastructure. Allure results from all jobs
  are merged into one report.
- Runs on `main` publish the report to <https://adrianilie1327.github.io/playwright-python-framework/>
  with history. PR runs attach it as an artifact. Every job uploads its HTML report, and failed jobs
  also upload Playwright traces, videos and screenshots.

## Conventions

- **Page objects** hold locators and user intents (`login`, `add_to_cart`). Assertions about
  business outcomes stay in tests. Navigation methods return the next page object, already loaded.
- **Locators** prefer `get_by_role` and `get_by_test_id`. The test-id attribute is set to `data-test`
  for this app in `tests/ui/conftest.py`. Use web-first `expect(...)` assertions instead of sleeps.
- **API tests** validate responses against Pydantic models in `framework/api/models.py`, so a
  changed contract fails loudly.
- **Test data**: static data goes in `test_data/*.json`. Unique data per run comes from
  `framework/utils/data_factory.py`.
- **Isolation**: every UI test gets a fresh browser context. API tests that need a clean session use
  `anonymous_auth_client`, because request contexts keep cookies.
- Tag every test with `smoke` or `regression`. The `ui`/`api` markers are added automatically from
  the folder.
