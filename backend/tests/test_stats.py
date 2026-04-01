"""Tests for GET /api/v1/stats/* — statistics endpoints."""

from httpx import AsyncClient

from app.models.herb import Herb

BASE = "/api/v1/stats"


# ---- /overview ----------------------------------------------------------


async def test_overview_empty(client: AsyncClient):
    resp = await client.get(f"{BASE}/overview")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_herbs"] == 0
    assert body["total_categories"] == 0
    assert body["latest_added"] is None


async def test_overview_with_data(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(f"{BASE}/overview")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_herbs"] == 5
    assert body["total_categories"] == 3  # 补气药, 清热药, 补血药
    assert body["latest_added"] is not None


# ---- /category-distribution --------------------------------------------


async def test_category_distribution(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(f"{BASE}/category-distribution")
    assert resp.status_code == 200

    data = resp.json()
    dist = {item["name"]: item["value"] for item in data}
    assert dist["补气药"] == 2
    assert dist["清热药"] == 2
    assert dist["补血药"] == 1


# ---- /nature-distribution -----------------------------------------------


async def test_nature_distribution(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(f"{BASE}/nature-distribution")
    assert resp.status_code == 200

    data = resp.json()
    dist = {item["name"]: item["value"] for item in data}
    assert dist["温"] == 2   # 黄芪, 当归
    assert dist["寒"] == 2   # 金银花, 黄连
    assert dist["平"] == 1   # 人参


# ---- /flavor-distribution -----------------------------------------------


async def test_flavor_distribution(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(f"{BASE}/flavor-distribution")
    assert resp.status_code == 200

    data = resp.json()
    dist = {item["name"]: item["value"] for item in data}

    # 甘 appears in: 黄芪, 人参, 金银花, 当归 → 4
    assert dist["甘"] == 4
    # 苦 appears in: 人参, 黄连 → 2
    assert dist["苦"] == 2
    # 辛 appears in: 当归 → 1
    assert dist["辛"] == 1
