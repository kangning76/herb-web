from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.recommendation import (
    HerbRecommendation,
    MatchReason,
    RecommendationListResponse,
)
from app.services import recommendation_service

router = APIRouter(prefix="/herbs", tags=["recommendations"])


@router.get(
    "/recommendations/explore",
    response_model=RecommendationListResponse,
)
async def explore_recommendations(
    category: str | None = None,
    nature: str | None = None,
    flavor: list[str] | None = Query(None),
    efficacy_keywords: str | None = None,
    limit: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    results = await recommendation_service.explore_recommendations(
        db,
        category=category,
        nature=nature,
        flavors=flavor,
        efficacy_keywords=efficacy_keywords,
        limit=limit,
    )
    items = [
        HerbRecommendation(
            herb=r["herb"],
            similarity_score=r["similarity_score"],
            match_reasons=[MatchReason(**mr) for mr in r["match_reasons"]],
        )
        for r in results
    ]
    return RecommendationListResponse(items=items, total=len(items))


@router.get(
    "/{herb_id}/recommendations",
    response_model=RecommendationListResponse,
)
async def get_herb_recommendations(
    herb_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    target, results = await recommendation_service.get_recommendations_for_herb(
        db, herb_id, limit=limit
    )
    if target is None:
        raise HTTPException(status_code=404, detail="Herb not found")

    items = [
        HerbRecommendation(
            herb=r["herb"],
            similarity_score=r["similarity_score"],
            match_reasons=[MatchReason(**mr) for mr in r["match_reasons"]],
        )
        for r in results
    ]
    return RecommendationListResponse(items=items, total=len(items))
