"""Tests for herb search and filtering under /api/v1/herbs."""

from httpx import AsyncClient

from app.models.herb import Herb

BASE = "/api/v1/herbs"

# All tests in this module use the ``multiple_herbs`` fixture which seeds:
#   黄芪  (补气药, 温, Huang Qi,   补气升阳)
#   人参  (补气药, 平, Ren Shen,   大补元气)
#   金银花 (清热药, 寒, Jin Yin Hua, 清热解毒)
#   黄连  (清热药, 寒, Huang Lian,  清热燥湿)
#   当归  (补血药, 温, Dang Gui,    补血活血)


# ── Full-text search (q=) ─────────────────────────────────────────────


async def test_search_by_name_cn(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(BASE, params={"q": "黄芪"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name_cn"] == "黄芪"


async def test_search_by_pinyin(client: AsyncClient, multiple_herbs: list[Herb]):
    """q=Huang matches name_pinyin for both Huang Qi and Huang Lian."""
    resp = await client.get(BASE, params={"q": "Huang"})
    assert resp.status_code == 200
    data = resp.json()
    names = {item["name_cn"] for item in data["items"]}
    assert data["total"] == 2
    assert names == {"黄芪", "黄连"}


async def test_search_by_efficacy(client: AsyncClient, multiple_herbs: list[Herb]):
    """q=补气 matches category '补气药' (黄芪, 人参) and efficacy '补气升阳' (黄芪)."""
    resp = await client.get(BASE, params={"q": "补气"})
    assert resp.status_code == 200
    data = resp.json()
    names = {item["name_cn"] for item in data["items"]}
    assert data["total"] == 2
    assert names == {"黄芪", "人参"}


async def test_search_no_results(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(BASE, params={"q": "不存在的药材"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


# ── Exact filters ─────────────────────────────────────────────────────


async def test_filter_by_category(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(BASE, params={"category": "清热药"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    names = {item["name_cn"] for item in data["items"]}
    assert names == {"金银花", "黄连"}
    # every returned item belongs to the requested category
    assert all(item["category"] == "清热药" for item in data["items"])


async def test_filter_by_nature(client: AsyncClient, multiple_herbs: list[Herb]):
    resp = await client.get(BASE, params={"nature": "寒"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    names = {item["name_cn"] for item in data["items"]}
    assert names == {"金银花", "黄连"}
    assert all(item["nature"] == "寒" for item in data["items"])


# ── Combined search + filter ──────────────────────────────────────────


async def test_combined_search_and_filter(client: AsyncClient, multiple_herbs: list[Herb]):
    """q=黄 narrows to 黄芪 and 黄连; category=清热药 keeps only 黄连."""
    resp = await client.get(BASE, params={"q": "黄", "category": "清热药"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name_cn"] == "黄连"
    assert data["items"][0]["category"] == "清热药"
