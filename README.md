# Playwright_Python

Playwright + pytest (Python) tests for https://automationexercise.com: browser UI tests and API tests.

```
tests/
  conftest.py        shared fixtures (API client, unique user data)
  api/               one spec file per API group (+ data masking tests)
  ui/                browser tests
utils/masking.py     synthetic customer-data masking (keeps the customer id)
TEST_LIST.md         full list of scenarios
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

## Run

```bash
pytest                      # everything
pytest tests/api            # API only (also: pytest -m api)
pytest tests/ui --browser firefox --headed
```

An HTML report is written to `reports/report.html`; failed UI tests keep a screenshot in `test-results/`.
Every API test also records its requests and responses: expand a test row in the report to see them in its log, or read them all in `reports/api_responses.json` (passwords are masked).

## CI

`.github/workflows/playwright.yml` runs the API tests and the UI tests per browser (chromium, firefox, webkit) on PRs, pushes to `main`, nightly and manually, uploading the reports as artifacts.
