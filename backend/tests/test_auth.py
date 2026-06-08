"""Teste unitare pentru serviciul de autentificare si securitate."""
from jose import jwt

from config import SECRET_KEY, ALGORITHM
from services.auth_service import (
    hash_password, verify_password,
    generate_reset_token, hash_reset_token,
    create_access_token,
)


def test_hash_password_differs_from_plain():
    assert hash_password("parola123") != "parola123"


def test_verify_password_accepts_correct():
    h = hash_password("parola123")
    assert verify_password("parola123", h) is True


def test_verify_password_rejects_wrong():
    h = hash_password("parola123")
    assert verify_password("altaparola", h) is False


def test_hash_password_is_salted():
    h1 = hash_password("aceeasi")
    h2 = hash_password("aceeasi")
    assert h1 != h2
    assert verify_password("aceeasi", h1)
    assert verify_password("aceeasi", h2)


def test_reset_token_hash_is_consistent():
    raw, token_hash = generate_reset_token()
    assert hash_reset_token(raw) == token_hash


def test_reset_token_is_unique():
    raw1, _ = generate_reset_token()
    raw2, _ = generate_reset_token()
    assert raw1 != raw2


def test_access_token_roundtrip_sub():
    token = create_access_token({"sub": 123})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "123"


def test_access_token_has_expiry():
    token = create_access_token({"sub": "1"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload
