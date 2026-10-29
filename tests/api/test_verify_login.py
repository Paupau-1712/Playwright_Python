"""API 7-10: verify login."""

import pytest

pytestmark = pytest.mark.api


def test_verify_login_with_valid_details(api, created_user):
    """API 7: valid email/password returns 200 'User exists!'."""
    body = api.post(
        "verifyLogin",
        form={"email": created_user["email"], "password": created_user["password"]},
    ).json()
    assert body["responseCode"] == 200
    assert body["message"] == "User exists!"


def test_verify_login_without_email(api):
    """API 8: missing email returns 400."""
    body = api.post("verifyLogin", form={"password": "whatever"}).json()
    assert body["responseCode"] == 400
    assert "email or password parameter is missing" in body["message"]


def test_delete_to_verify_login_is_not_supported(api):
    """API 9: DELETE /verifyLogin returns 405."""
    body = api.delete("verifyLogin").json()
    assert body["responseCode"] == 405
    assert body["message"] == "This request method is not supported."


def test_verify_login_with_invalid_details(api):
    """API 10: unknown credentials return 404 'User not found!'."""
    body = api.post(
        "verifyLogin",
        form={"email": "nobody_here@example.com", "password": "wrong"},
    ).json()
    assert body["responseCode"] == 404
    assert body["message"] == "User not found!"
