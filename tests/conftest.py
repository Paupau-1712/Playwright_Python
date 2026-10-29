import uuid

import pytest

BASE_URL = "https://automationexercise.com"
API_URL = f"{BASE_URL}/api/"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def api(playwright):
    """Playwright APIRequestContext pointed at the Automation Exercise API."""
    context = playwright.request.new_context(base_url=API_URL, timeout=60_000)
    yield context
    context.dispose()


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
