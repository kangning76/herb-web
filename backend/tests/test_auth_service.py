"""Unit tests for app.services.auth_service (no DB / no HTTP client needed)."""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


# ---------------------------------------------------------------------------
# hash_password / verify_password
# ---------------------------------------------------------------------------

def test_hash_password_returns_bcrypt_string():
    hashed = hash_password("mypassword")
    # bcrypt hashes are 60 chars and start with "$2b$"
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$")
    assert len(hashed) == 60


def test_verify_password_correct():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("wrong-password", hashed) is False


# ---------------------------------------------------------------------------
# create_access_token / create_refresh_token / decode_token
# ---------------------------------------------------------------------------

def test_create_access_token_decodable():
    token = create_access_token("alice")
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "alice"
    assert payload["type"] == "access"
    # exp should be ~30 min from now
    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    delta = exp_dt - datetime.now(timezone.utc)
    assert timedelta(minutes=29) < delta <= timedelta(minutes=31)


def test_create_refresh_token_has_refresh_type():
    token = create_refresh_token("bob")
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "bob"
    assert payload["type"] == "refresh"
    # exp should be ~7 days from now
    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    delta = exp_dt - datetime.now(timezone.utc)
    assert timedelta(days=6, hours=23) < delta <= timedelta(days=7, minutes=1)


def test_decode_token_invalid_returns_none():
    assert decode_token("not-a-real-jwt") is None
    assert decode_token("") is None


def test_decode_token_expired_returns_none():
    """Manually craft a token that expired 1 hour ago."""
    expired_payload = {
        "sub": "expired-user",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "type": "access",
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm="HS256")
    assert decode_token(expired_token) is None
