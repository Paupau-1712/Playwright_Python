"""API 5 & 6: search product."""

import pytest

pytestmark = pytest.mark.api


@pytest.mark.parametrize("term", ["top", "tshirt", "jean"])
def test_search_product(api, term):
    """API 5: POST /searchProduct with search_product returns matching products."""
    body = api.post("searchProduct", form={"search_product": term}).json()
    assert body["responseCode"] == 200
    assert len(body["products"]) > 0


def test_search_product_without_parameter(api):
    """API 6: POST /searchProduct without search_product returns 400."""
    body = api.post("searchProduct").json()
    assert body["responseCode"] == 400
    assert "search_product parameter is missing" in body["message"]
