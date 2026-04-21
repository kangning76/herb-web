import re
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.herb import Herb

# Weights for each similarity dimension (must sum to 1.0)
W_CATEGORY = 0.35
W_EFFICACY = 0.25
W_NATURE = 0.20
W_FLAVOR = 0.20

# Punctuation pattern used to split efficacy text into keywords
_PUNCT_RE = re.compile(r"[，,、；;。\s]+")


def _split_efficacy(text: str | None) -> set[str]:
    """Split efficacy text into a set of keywords by Chinese/English punctuation."""
    if not text:
        return set()
    return {w for w in _PUNCT_RE.split(text.strip()) if w}


def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _compute_similarity(
    target_category: str | None,
    target_nature: str | None,
    target_flavors: set[str],
    target_efficacy_kw: set[str],
    herb: Herb,
) -> tuple[float, list[dict]]:
    """Compute similarity score (0-100) and match reasons for a candidate herb."""
    score = 0.0
    reasons: list[dict] = []

    # Category
    if target_category and herb.category == target_category:
        score += W_CATEGORY * 100
        reasons.append({"dimension": "category", "label": f"同分类：{herb.category}"})

    # Nature
    if target_nature and herb.nature == target_nature:
        score += W_NATURE * 100
        reasons.append({"dimension": "nature", "label": f"同药性：{herb.nature}"})

    # Flavor (Jaccard)
    herb_flavors = set(herb.flavor) if herb.flavor else set()
    if target_flavors and herb_flavors:
        flavor_sim = _jaccard(target_flavors, herb_flavors)
        if flavor_sim > 0:
            score += W_FLAVOR * 100 * flavor_sim
            common = target_flavors & herb_flavors
            reasons.append({"dimension": "flavor", "label": f"共同药味：{'、'.join(sorted(common))}"})

    # Efficacy (Jaccard on keyword sets)
    herb_kw = _split_efficacy(herb.efficacy)
    if target_efficacy_kw and herb_kw:
        eff_sim = _jaccard(target_efficacy_kw, herb_kw)
        if eff_sim > 0:
            score += W_EFFICACY * 100 * eff_sim
            common_kw = target_efficacy_kw & herb_kw
            top_kw = sorted(common_kw)[:3]
            reasons.append({"dimension": "efficacy", "label": f"相似功效：{'、'.join(top_kw)}"})

    return round(score, 1), reasons


async def get_recommendations_for_herb(
    db: AsyncSession,
    herb_id: int,
    limit: int = 6,
) -> tuple[Herb | None, list[dict]]:
    """Get similar herbs for a given herb.

    Returns (target_herb, recommendations) where each recommendation is a dict
    with keys: herb, similarity_score, match_reasons.
    Returns (None, []) if the target herb is not found.
    """
    result = await db.execute(select(Herb).where(Herb.id == herb_id))
    target = result.scalar_one_or_none()
    if not target:
        return None, []

    # Fetch all other herbs
    result = await db.execute(select(Herb).where(Herb.id != herb_id))
    candidates: Sequence[Herb] = result.scalars().all()

    target_flavors = set(target.flavor) if target.flavor else set()
    target_kw = _split_efficacy(target.efficacy)

    scored: list[dict] = []
    for herb in candidates:
        sim_score, reasons = _compute_similarity(
            target.category, target.nature, target_flavors, target_kw, herb
        )
        if sim_score > 0:
            scored.append({
                "herb": herb,
                "similarity_score": sim_score,
                "match_reasons": reasons,
            })

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return target, scored[:limit]


async def explore_recommendations(
    db: AsyncSession,
    *,
    category: str | None = None,
    nature: str | None = None,
    flavors: list[str] | None = None,
    efficacy_keywords: str | None = None,
    limit: int = 12,
) -> list[dict]:
    """Explore herbs matching user-selected criteria.

    Returns a list of dicts with keys: herb, similarity_score, match_reasons.
    """
    result = await db.execute(select(Herb))
    all_herbs: Sequence[Herb] = result.scalars().all()

    target_flavors = set(flavors) if flavors else set()
    target_kw = set()
    if efficacy_keywords:
        target_kw = {w for w in efficacy_keywords.strip().split() if w}

    scored: list[dict] = []
    for herb in all_herbs:
        sim_score, reasons = _compute_similarity(
            category, nature, target_flavors, target_kw, herb
        )
        if sim_score > 0:
            scored.append({
                "herb": herb,
                "similarity_score": sim_score,
                "match_reasons": reasons,
            })

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored[:limit]
