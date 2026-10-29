import json
import time
import uuid
from pathlib import Path

import pytest

BASE_URL = "https://automationexercise.com"
API_URL = f"{BASE_URL}/api/"
RESPONSES_FILE = Path("reports/api_responses.json")

# test node id -> list of recorded API calls, written to RESPONSES_FILE at the end
all_api_calls = {}


class RecordingAPI:
    """Wraps an APIRequestContext and records every request/response pair."""

    def __init__(self, context, calls):
        self._context = context
        self.calls = calls

    def _send(self, method, path, **kwargs):
        # The site sometimes answers with an HTML "heavy load" page; retry until JSON comes back.
        for attempt in range(4):
            response = self._context.fetch(path, method=method, **kwargs)
            if response.text().lstrip().startswith("{"):
                break
            time.sleep(2 * (attempt + 1))
        sent = kwargs.get("form") or kwargs.get("params") or {}
        call = {
            "request": f"{method} {API_URL}{path}",
            "sent": {k: ("***" if k == "password" else v) for k, v in sent.items()},
            "http_status": response.status,
            "response": response.text(),
        }
        self.calls.append(call)
        # Captured stdout is shown in each test's log in the HTML report, even when it passes.
        print(
            f"{call['request']}\nsent: {json.dumps(call['sent'])}\n"
            f"HTTP {call['http_status']}\n{call['response']}\n"
        )
        return response

    def get(self, path, **kwargs):
        return self._send("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._send("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._send("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._send("DELETE", path, **kwargs)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def api_context(playwright):
    """Playwright APIRequestContext pointed at the Automation Exercise API."""
    context = playwright.request.new_context(base_url=API_URL, timeout=60_000)
    yield context
    context.dispose()


@pytest.fixture
def api(api_context, request):
    calls = all_api_calls.setdefault(request.node.nodeid, [])
    return RecordingAPI(api_context, calls)


def pytest_sessionfinish(session):
    if all_api_calls:
        RESPONSES_FILE.parent.mkdir(exist_ok=True)
        RESPONSES_FILE.write_text(json.dumps(all_api_calls, indent=2))


@pytest.fixture
def user_payload():
    """Unique user data so repeated runs never collide."""
    unique = uuid.uuid4().hex[:10]
    return {
        "name": f"qa_{unique}",
        "email": f"qa_{unique}@example.com",
        "password": "Passw0rd!123",
        "title": "Mr",
        "birth_date": "10",
        "birth_month": "May",
        "birth_year": "1990",
        "firstname": "QA",
        "lastname": "Tester",
        "company": "Example Co",
        "address1": "1 Test Street",
        "address2": "Suite 2",
        "country": "Singapore",
        "zipcode": "123456",
        "state": "Central",
        "city": "Singapore",
        "mobile_number": "81234567",
    }


@pytest.fixture
def created_user(api, user_payload):
    """Registers a user through the API and deletes it afterwards."""
    response = api.post("createAccount", form=user_payload)
    assert response.json()["responseCode"] == 201
    yield user_payload
    api.delete(
        "deleteAccount",
        form={"email": user_payload["email"], "password": user_payload["password"]},
    )
