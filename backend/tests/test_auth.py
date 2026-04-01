"""API integration tests for /api/v1/auth endpoints."""

from httpx import AsyncClient

AUTH_PREFIX = "/api/v1/auth"


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------

async def test_login_success(client: AsyncClient, admin_user):
    resp = await client.post(
        f"{AUTH_PREFIX}/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, admin_user):
    resp = await client.post(
        f"{AUTH_PREFIX}/login",
        json={"username": "testadmin", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post(
        f"{AUTH_PREFIX}/login",
        json={"username": "no_such_user", "password": "whatever"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /refresh
# ---------------------------------------------------------------------------

async def test_refresh_token_success(client: AsyncClient, admin_user):
    # First login to obtain tokens
    login_resp = await client.post(
        f"{AUTH_PREFIX}/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Use the refresh token to get new tokens
    resp = await client.post(
        f"{AUTH_PREFIX}/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_refresh_with_access_token_fails(client: AsyncClient, admin_user):
    """An access token must NOT be accepted as a refresh token."""
    login_resp = await client.post(
        f"{AUTH_PREFIX}/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        f"{AUTH_PREFIX}/refresh",
        json={"refresh_token": access_token},
    )
    assert resp.status_code == 401


async def test_refresh_with_invalid_token_fails(client: AsyncClient):
    resp = await client.post(
        f"{AUTH_PREFIX}/refresh",
        json={"refresh_token": "garbage.token.value"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------

async def test_logout(client: AsyncClient):
    resp = await client.post(f"{AUTH_PREFIX}/logout")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Logged out successfully"


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------

async def test_me_authenticated(auth_client: AsyncClient, admin_user):
    resp = await auth_client.get(f"{AUTH_PREFIX}/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "testadmin"
    assert "id" in body


async def test_me_unauthenticated(client: AsyncClient):
    """Without a Bearer token, HTTPBearer returns 403."""
    resp = await client.get(f"{AUTH_PREFIX}/me")
    assert resp.status_code == 403
