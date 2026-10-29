import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def test_home_page_title(page: Page):
    page.goto("/")
    expect(page).to_have_title("Automation Exercise")


def test_products_page_lists_products(page: Page):
    # Direct navigation: the site's ad overlays can intercept nav-link clicks.
    page.goto("/products")
    expect(page.get_by_role("heading", name="All Products")).to_be_visible()
    expect(page.locator(".features_items .product-image-wrapper").first).to_be_visible()


def test_login_page_is_reachable(page: Page):
    page.goto("/login")
    expect(page.get_by_role("heading", name="Login to your account")).to_be_visible()
