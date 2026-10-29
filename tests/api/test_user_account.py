"""API 11-14: create, delete, update and fetch a user account."""

import pytest

pytestmark = pytest.mark.api


def test_create_account(api, user_payload):
    """API 11: POST /createAccount returns 201 'User created!'."""
    try:
        body = api.post("createAccount", form=user_payload).json()
        assert body["responseCode"] == 201
        assert body["message"] == "User created!"
    finally:
        api.delete(
            "deleteAccount",
            form={"email": user_payload["email"], "password": user_payload["password"]},
        )


def test_delete_account(api, user_payload):
    """API 12: DELETE /deleteAccount returns 200 'Account deleted!'."""
    api.post("createAccount", form=user_payload)
    body = api.delete(
        "deleteAccount",
        form={"email": user_payload["email"], "password": user_payload["password"]},
    ).json()
    assert body["responseCode"] == 200
    assert body["message"] == "Account deleted!"


def test_update_account(api, created_user):
    """API 13: PUT /updateAccount returns 200 'User updated!'."""
    updated = {**created_user, "city": "Updated City"}
    body = api.put("updateAccount", form=updated).json()
    assert body["responseCode"] == 200
    assert body["message"] == "User updated!"


def test_get_user_detail_by_email(api, created_user):
    """API 14: GET /getUserDetailByEmail returns the user's details."""
    body = api.get("getUserDetailByEmail", params={"email": created_user["email"]}).json()
    assert body["responseCode"] == 200
    assert body["user"]["email"] == created_user["email"]
    assert body["user"]["name"] == created_user["name"]


def test_get_user_detail_for_unknown_email(api):
    """API 14 (negative): unknown email returns 404."""
    body = api.get("getUserDetailByEmail", params={"email": "nobody_here@example.com"}).json()
    assert body["responseCode"] == 404
