"""Data masking on a GET response: original in, regex-masked synthetic data out, id retained."""

import json
import re
from pathlib import Path

import pytest

from utils.masking import comparison_html, flatten, mask_record, render_text_table

pytestmark = pytest.mark.api

COLUMNS = ["id", "name", "brand", "category.usertype.usertype", "category.category", "price"]
MASKED_FIELDS = COLUMNS[1:]
SAMPLE_SIZE = 20
COMPARISON_FILE = Path("reports/masking_comparison.html")


@pytest.fixture(scope="module")
def products(api_context):
    """Original records straight from GET /productsList."""
    body = api_context.get("productsList").json()
    assert body["responseCode"] == 200
    return body["products"][:SAMPLE_SIZE]


@pytest.fixture
def masked_products(products):
    return [mask_record(p) for p in products]


def test_get_products_response(api):
    """Fetch the original data with GET only and show the response."""
    response = api.get("productsList")
    assert response.status == 200
    body = response.json()
    assert body["responseCode"] == 200
    print(json.dumps(body["products"][:3], indent=2))
    assert len(body["products"]) > 0


def test_input_and_masked_output_comparison(products, masked_products):
    """Show original vs masked side by side, like a production-to-masked comparison."""
    original_rows = [flatten(p) for p in products]
    masked_rows = [flatten(p) for p in masked_products]

    print(render_text_table("FROM PRODUCTION DATA", original_rows, COLUMNS))
    print()
    print(render_text_table("TO SYNTHETICALLY IDENTICAL MASKED DATA", masked_rows, COLUMNS))

    COMPARISON_FILE.parent.mkdir(exist_ok=True)
    COMPARISON_FILE.write_text(comparison_html(original_rows, masked_rows, COLUMNS))

    assert len(original_rows) == len(masked_rows) == len(products)


def test_id_is_retained(products, masked_products):
    assert [m["id"] for m in masked_products] == [p["id"] for p in products]


def test_every_masked_field_differs_from_the_input(products, masked_products):
    for original, masked in zip(products, masked_products):
        o, m = flatten(original), flatten(masked)
        for field in MASKED_FIELDS:
            assert m[field] != o[field], f"id {original['id']}: {field} was not masked"


def test_masked_values_keep_the_original_format(products, masked_products):
    """Same shape: letters stay letters, digits stay digits, punctuation/spaces untouched."""

    def shape(value):
        return re.sub(r"[A-Z]", "A", re.sub(r"[a-z]", "a", re.sub(r"\d", "9", value)))

    for original, masked in zip(products, masked_products):
        o, m = flatten(original), flatten(masked)
        for field in MASKED_FIELDS:
            if field == "price":
                assert m[field].startswith("Rs. ")
                assert shape(m[field]) == shape(o[field])
            else:
                assert shape(m[field]) == shape(o[field]), field


def test_no_original_value_appears_in_the_output(products, masked_products):
    output = json.dumps(masked_products)
    for product in products:
        assert product["name"] not in output
        assert product["price"] not in output


def test_masking_is_deterministic(products):
    assert [mask_record(p) for p in products] == [mask_record(p) for p in products]


def test_masking_does_not_modify_the_input(products):
    snapshot = json.loads(json.dumps(products))
    for product in products:
        mask_record(product)
    assert products == snapshot
