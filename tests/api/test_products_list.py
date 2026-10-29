"""API 1 & 2: products list."""

import pytest

pytestmark = pytest.mark.api


def test_get_all_products_list(api):
    """API 1: GET /productsList returns 200 and a non-empty list."""
    body = api.get("productsList").json()
    assert body["responseCode"] == 200
    assert len(body["products"]) > 0
    assert {"id", "name", "price", "brand", "category"} <= body["products"][0].keys()


def test_post_to_products_list_is_not_supported(api):
    """API 2: POST /productsList returns 405."""
    body = api.post("productsList").json()
    assert body["responseCode"] == 405
    assert body["message"] == "This request method is not supported."
