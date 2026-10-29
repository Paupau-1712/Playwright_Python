"""Data masking on a GET response: original in, regex-masked synthetic data out, id retained."""

import json
import re
from pathlib import Path

import pytest

from utils.masking import (
    NUMERIC_FIELDS,
    comparison_html,
    flatten,
    mask_record,
    mask_records,
    render_text_table,
)

pytestmark = pytest.mark.api

COLUMNS = ["id", "name", "brand", "category.usertype.usertype", "category.category", "price"]
MASKED_FIELDS = COLUMNS[1:]
STRING_FIELDS = [c for c in MASKED_FIELDS if c not in NUMERIC_FIELDS]
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
    return mask_records(products)


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
    assert mask_records(products) == mask_records(products)


def test_masking_does_not_modify_the_input(products):
    snapshot = json.loads(json.dumps(products))
    for product in products:
        mask_record(product)
    assert products == snapshot


def test_string_columns_are_unique_after_masking(masked_products):
    """Names, brands, categories: every masked value in a column is unique and synthetic."""
    flat = [flatten(p) for p in masked_products]
    for field in STRING_FIELDS:
        values = [row[field] for row in flat]
        assert len(set(values)) == len(values), f"{field} has duplicate masked values"


def test_masked_price_never_starts_with_zero(products, masked_products):
    for original, masked in zip(products, masked_products):
        amount = re.search(r"\d+", masked["price"]).group()
        assert amount[0] != "0", f"id {original['id']}: {masked['price']}"


def test_price_first_digit_is_never_zero_across_many_seeds(products):
    for secret in (f"salt-{i}" for i in range(200)):
        for product in mask_records(products, secret):
            assert re.search(r"\d", product["price"]).group() != "0"
