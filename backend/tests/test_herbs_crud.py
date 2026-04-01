"""Tests for herb CRUD endpoints under /api/v1/herbs."""

from httpx import AsyncClient

from app.models.herb import Herb

BASE = "/api/v1/herbs"

NEW_HERB = {
    "name_cn": "白术",
    "name_pinyin": "Bai Zhu",
    "category": "补气药",
    "nature": "温",
    "flavor": ["甘", "苦"],
    "efficacy": "健脾益气，燥湿利水",
}


# ── Create ────────────────────────────────────────────────────────────


async def test_create_herb(auth_client: AsyncClient):
    resp = await auth_client.post(BASE, json=NEW_HERB)
    assert resp.status_code == 201

    data = resp.json()
    assert data["name_cn"] == NEW_HERB["name_cn"]
    assert data["name_pinyin"] == NEW_HERB["name_pinyin"]
    assert data["category"] == NEW_HERB["category"]
    assert data["nature"] == NEW_HERB["nature"]
    assert data["flavor"] == NEW_HERB["flavor"]
    assert data["efficacy"] == NEW_HERB["efficacy"]
    assert isinstance(data["id"], int)
    assert "created_at" in data
    assert "updated_at" in data
    assert data["image_url"] is None


async def test_create_herb_unauthenticated(client: AsyncClient):
    resp = await client.post(BASE, json=NEW_HERB)
    assert resp.status_code in (401, 403)


async def test_create_herb_duplicate_name(auth_client: AsyncClient):
    resp1 = await auth_client.post(BASE, json=NEW_HERB)
    assert resp1.status_code == 201

    resp2 = await auth_client.post(BASE, json=NEW_HERB)
    assert resp2.status_code >= 400  # unique constraint violation


# ── Read ──────────────────────────────────────────────────────────────


async def test_get_herb(auth_client: AsyncClient):
    create_resp = await auth_client.post(BASE, json=NEW_HERB)
    assert create_resp.status_code == 201
    herb_id = create_resp.json()["id"]

    resp = await auth_client.get(f"{BASE}/{herb_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == herb_id
    assert data["name_cn"] == NEW_HERB["name_cn"]
    assert data["category"] == NEW_HERB["category"]


async def test_get_herb_not_found(client: AsyncClient):
    resp = await client.get(f"{BASE}/99999")
    assert resp.status_code == 404


async def test_list_herbs_empty(client: AsyncClient):
    resp = await client.get(BASE)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["total_pages"] == 0


async def test_list_herbs_paginated(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(BASE, params={"page": 1, "page_size": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3  # ceil(5 / 2)


async def test_list_herbs_sort_by_name(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(BASE, params={"sort_by": "name_cn", "order": "asc"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 5
    names = [item["name_cn"] for item in items]
    assert names == sorted(names), "Items should be sorted by name_cn ascending"


# ── Update ────────────────────────────────────────────────────────────


async def test_update_herb(auth_client: AsyncClient):
    create_resp = await auth_client.post(BASE, json=NEW_HERB)
    assert create_resp.status_code == 201
    herb_id = create_resp.json()["id"]

    resp = await auth_client.put(
        f"{BASE}/{herb_id}",
        json={"name_pinyin": "Bai Zhu Updated"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name_pinyin"] == "Bai Zhu Updated"
    assert data["name_cn"] == NEW_HERB["name_cn"]  # unchanged


async def test_update_herb_not_found(auth_client: AsyncClient):
    resp = await auth_client.put(f"{BASE}/99999", json={"name_pinyin": "X"})
    assert resp.status_code == 404


# ── Delete ────────────────────────────────────────────────────────────


async def test_delete_herb(auth_client: AsyncClient):
    create_resp = await auth_client.post(BASE, json=NEW_HERB)
    assert create_resp.status_code == 201
    herb_id = create_resp.json()["id"]

    del_resp = await auth_client.delete(f"{BASE}/{herb_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Herb deleted"

    get_resp = await auth_client.get(f"{BASE}/{herb_id}")
    assert get_resp.status_code == 404


async def test_delete_herb_unauthenticated(client: AsyncClient, sample_herb: Herb):
    resp = await client.delete(f"{BASE}/{sample_herb.id}")
    assert resp.status_code in (401, 403)


# ── Categories ────────────────────────────────────────────────────────


async def test_get_categories(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(f"{BASE}/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert set(data) == {"补气药", "清热药", "补血药"}
