"""Data masking: original customer data in, synthetic data out, customer id retained."""

import json
import re

import pytest

from utils.masking import mask_customer

pytestmark = pytest.mark.api

PII_FIELDS = [
    "name", "email", "first_name", "last_name", "company", "address1", "address2",
    "city", "state", "zipcode", "birth_day", "birth_month", "birth_year",
]  # fmt: skip


@pytest.fixture
def original(api, created_user):
    """The original customer record, as returned by the live API."""
    body = api.get("getUserDetailByEmail", params={"email": created_user["email"]}).json()
    assert body["responseCode"] == 200
    return body["user"]


def test_customer_id_is_retained(original):
    masked = mask_customer(original)
    assert masked["id"] == original["id"]


def test_personal_fields_are_replaced_with_synthetic_data(original):
    masked = mask_customer(original)
    for field in PII_FIELDS:
        assert masked[field] != original[field], f"{field} was not masked"


def test_no_original_value_leaks_into_output(original):
    masked = json.dumps(mask_customer(original))
    for field in ["name", "email", "first_name", "last_name", "company", "address1"]:
        assert original[field] not in masked, f"original {field} leaked"


def test_masked_data_is_well_formed(original):
    masked = mask_customer(original)
    assert re.fullmatch(r"[^@\s]+@masked\.example\.com", masked["email"])
    assert masked["name"] == f"{masked['first_name']} {masked['last_name']}"
    assert re.fullmatch(r"\d{5}", masked["zipcode"])
    assert 1 <= int(masked["birth_day"]) <= 28


def test_masking_is_deterministic_per_customer(original):
    assert mask_customer(original) == mask_customer(original)


def test_different_customers_get_different_masked_data(original):
    other = {**original, "id": original["id"] + 1}
    assert mask_customer(other)["email"] != mask_customer(original)["email"]


def test_masking_does_not_modify_the_original(original):
    snapshot = dict(original)
    mask_customer(original)
    assert original == snapshot


def test_non_personal_fields_are_preserved(original):
    masked = mask_customer(original)
    assert masked["title"] == original["title"]
    assert masked["country"] == original["country"]
