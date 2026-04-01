"""Tests for POST /api/v1/herbs/{id}/image — herb image upload."""

from httpx import AsyncClient

from app.models.herb import Herb

API = "/api/v1/herbs"

# Minimal valid JPEG: SOI marker + APP0 padding + EOI marker.
TINY_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100 + b"\xff\xd9"


async def test_upload_image_success(auth_client: AsyncClient, sample_herb: Herb):
    url = f"{API}/{sample_herb.id}/image"
    files = {"file": ("photo.jpg", TINY_JPEG, "image/jpeg")}

    resp = await auth_client.post(url, files=files)
    assert resp.status_code == 200

    body = resp.json()
    assert body["image_url"] is not None
    assert body["image_url"].startswith("/uploads/herbs/")
    assert body["id"] == sample_herb.id


async def test_upload_image_wrong_type(auth_client: AsyncClient, sample_herb: Herb):
    url = f"{API}/{sample_herb.id}/image"
    files = {"file": ("notes.txt", b"hello world", "text/plain")}

    resp = await auth_client.post(url, files=files)
    assert resp.status_code == 400


async def test_upload_image_not_found(auth_client: AsyncClient):
    url = f"{API}/99999/image"
    files = {"file": ("photo.jpg", TINY_JPEG, "image/jpeg")}

    resp = await auth_client.post(url, files=files)
    assert resp.status_code == 404


async def test_upload_image_unauthenticated(client: AsyncClient, sample_herb: Herb):
    url = f"{API}/{sample_herb.id}/image"
    files = {"file": ("photo.jpg", TINY_JPEG, "image/jpeg")}

    resp = await client.post(url, files=files)
    assert resp.status_code in (401, 403)
