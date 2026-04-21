import pytest
from httpx import AsyncClient

from app.models.herb import Herb


@pytest.mark.asyncio
async def test_recommendations_for_herb(client: AsyncClient, multiple_herbs):
    """Recommendations for an existing herb return scored results."""
    target = multiple_herbs[0]  # 黄芪: 补气药, 温, [甘]
    resp = await client.get(f"/api/v1/herbs/{target.id}/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0

    # 人参 (补气药, 平, [甘, 苦]) should be the top recommendation
    top = data["items"][0]
    assert top["similarity_score"] > 0
    assert top["herb"]["name_cn"] == "人参"
    assert any(r["dimension"] == "category" for r in top["match_reasons"])


@pytest.mark.asyncio
async def test_recommendations_match_reasons(client: AsyncClient, multiple_herbs):
    """Match reasons include expected dimensions."""
    target = multiple_herbs[0]  # 黄芪: 补气药, 温, [甘]
    resp = await client.get(f"/api/v1/herbs/{target.id}/recommendations")
    data = resp.json()

    for item in data["items"]:
        for reason in item["match_reasons"]:
            assert "dimension" in reason
            assert "label" in reason
            assert reason["dimension"] in ("category", "nature", "flavor", "efficacy")


@pytest.mark.asyncio
async def test_recommendations_not_found(client: AsyncClient):
    """Recommendations for a non-existent herb return 404."""
    resp = await client.get("/api/v1/herbs/99999/recommendations")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_recommendations_limit(client: AsyncClient, multiple_herbs):
    """Limit parameter controls result count."""
    target = multiple_herbs[0]
    resp = await client.get(f"/api/v1/herbs/{target.id}/recommendations?limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_recommendations_excludes_self(client: AsyncClient, multiple_herbs):
    """Target herb is not included in its own recommendations."""
    target = multiple_herbs[0]
    resp = await client.get(f"/api/v1/herbs/{target.id}/recommendations")
    data = resp.json()
    ids = [item["herb"]["id"] for item in data["items"]]
    assert target.id not in ids


@pytest.mark.asyncio
async def test_recommendations_sorted_by_score(client: AsyncClient, multiple_herbs):
    """Results are sorted by similarity_score descending."""
    target = multiple_herbs[0]
    resp = await client.get(f"/api/v1/herbs/{target.id}/recommendations")
    data = resp.json()
    scores = [item["similarity_score"] for item in data["items"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_explore_by_category(client: AsyncClient, multiple_herbs):
    """Explore endpoint filters by category."""
    resp = await client.get("/api/v1/herbs/recommendations/explore?category=补气药")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["herb"]["category"] == "补气药"


@pytest.mark.asyncio
async def test_explore_by_nature(client: AsyncClient, multiple_herbs):
    """Explore endpoint filters by nature."""
    resp = await client.get("/api/v1/herbs/recommendations/explore?nature=寒")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["herb"]["nature"] == "寒"


@pytest.mark.asyncio
async def test_explore_by_flavor(client: AsyncClient, multiple_herbs):
    """Explore endpoint filters by flavor."""
    resp = await client.get("/api/v1/herbs/recommendations/explore?flavor=苦")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert any(r["dimension"] == "flavor" for r in item["match_reasons"])


@pytest.mark.asyncio
async def test_explore_by_efficacy_keywords(client: AsyncClient, multiple_herbs):
    """Explore endpoint filters by efficacy keywords."""
    resp = await client.get("/api/v1/herbs/recommendations/explore?efficacy_keywords=补气")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0


@pytest.mark.asyncio
async def test_explore_multiple_criteria(client: AsyncClient, multiple_herbs):
    """Explore with multiple criteria combines scores."""
    resp = await client.get(
        "/api/v1/herbs/recommendations/explore?category=补气药&nature=温&flavor=甘"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    top = data["items"][0]
    # Should have high score with multiple match reasons
    assert top["similarity_score"] > 50
    assert len(top["match_reasons"]) >= 2


@pytest.mark.asyncio
async def test_explore_no_criteria(client: AsyncClient, multiple_herbs):
    """Explore with no criteria returns empty results."""
    resp = await client.get("/api/v1/herbs/recommendations/explore")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_explore_limit(client: AsyncClient, multiple_herbs):
    """Explore limit parameter controls result count."""
    resp = await client.get("/api/v1/herbs/recommendations/explore?category=补气药&limit=1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 1


@pytest.mark.asyncio
async def test_explore_sorted_by_score(client: AsyncClient, multiple_herbs):
    """Explore results sorted by similarity_score descending."""
    resp = await client.get("/api/v1/herbs/recommendations/explore?category=补气药")
    data = resp.json()
    scores = [item["similarity_score"] for item in data["items"]]
    assert scores == sorted(scores, reverse=True)
