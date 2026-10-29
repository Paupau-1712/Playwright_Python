"""API 3 & 4: brands list."""

import pytest

pytestmark = pytest.mark.api


def test_get_all_brands_list(api):
    """API 3: GET /brandsList returns 200 and a non-empty list."""
    body = api.get("brandsList").json()
    assert body["responseCode"] == 200
    assert len(body["brands"]) > 0
    assert {"id", "brand"} <= body["brands"][0].keys()


def test_put_to_brands_list_is_not_supported(api):
    """API 4: PUT /brandsList returns 405."""
    body = api.put("brandsList").json()
    assert body["responseCode"] == 405
    assert body["message"] == "This request method is not supported."
