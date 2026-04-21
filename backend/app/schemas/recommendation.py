from pydantic import BaseModel

from app.schemas.herb import HerbResponse


class MatchReason(BaseModel):
    dimension: str
    label: str


class HerbRecommendation(BaseModel):
    herb: HerbResponse
    similarity_score: float
    match_reasons: list[MatchReason]


class RecommendationListResponse(BaseModel):
    items: list[HerbRecommendation]
    total: int
