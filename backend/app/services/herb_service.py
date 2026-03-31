import csv
import io
import math
from typing import Sequence

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.herb import Herb
from app.schemas.herb import HerbCreate, HerbUpdate


async def get_herbs(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    category: str | None = None,
    nature: str | None = None,
    q: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> tuple[Sequence[Herb], int]:
    query = select(Herb)
    count_query = select(func.count(Herb.id))

    if category:
        query = query.where(Herb.category == category)
        count_query = count_query.where(Herb.category == category)
    if nature:
        query = query.where(Herb.nature == nature)
        count_query = count_query.where(Herb.nature == nature)
    if q:
        pattern = f"%{q}%"
        search_filter = or_(
            Herb.name_cn.ilike(pattern),
            Herb.name_pinyin.ilike(pattern),
            Herb.category.ilike(pattern),
            Herb.efficacy.ilike(pattern),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    sort_col = getattr(Herb, sort_by, Herb.created_at)
    if order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    total = (await db.execute(count_query)).scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_herb_by_id(db: AsyncSession, herb_id: int) -> Herb | None:
    result = await db.execute(select(Herb).where(Herb.id == herb_id))
    return result.scalar_one_or_none()


async def create_herb(db: AsyncSession, data: HerbCreate) -> Herb:
    herb = Herb(**data.model_dump())
    db.add(herb)
    await db.commit()
    await db.refresh(herb)
    return herb


async def update_herb(db: AsyncSession, herb: Herb, data: HerbUpdate) -> Herb:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(herb, key, value)
    await db.commit()
    await db.refresh(herb)
    return herb


async def delete_herb(db: AsyncSession, herb: Herb) -> None:
    await db.delete(herb)
    await db.commit()


async def get_categories(db: AsyncSession) -> list[str]:
    result = await db.execute(
        select(Herb.category).distinct().order_by(Herb.category)
    )
    return [row[0] for row in result.all()]


async def get_category_distribution(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Herb.category, func.count(Herb.id))
        .group_by(Herb.category)
        .order_by(func.count(Herb.id).desc())
    )
    return [{"name": row[0], "value": row[1]} for row in result.all()]


async def get_nature_distribution(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Herb.nature, func.count(Herb.id))
        .where(Herb.nature.is_not(None))
        .group_by(Herb.nature)
        .order_by(func.count(Herb.id).desc())
    )
    return [{"name": row[0], "value": row[1]} for row in result.all()]


async def get_flavor_distribution(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("SELECT unnest(flavor) AS f, COUNT(*) AS c FROM herbs GROUP BY f ORDER BY c DESC")
    )
    return [{"name": row[0], "value": row[1]} for row in result.all()]


async def get_overview(db: AsyncSession) -> dict:
    total = (await db.execute(select(func.count(Herb.id)))).scalar() or 0
    cat_count = (await db.execute(select(func.count(func.distinct(Herb.category))))).scalar() or 0
    latest = (await db.execute(select(func.max(Herb.created_at)))).scalar()
    return {
        "total_herbs": total,
        "total_categories": cat_count,
        "latest_added": latest.isoformat() if latest else None,
    }


async def import_herbs_from_csv(db: AsyncSession, csv_content: str) -> dict:
    reader = csv.DictReader(io.StringIO(csv_content))
    success_count = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            name_cn = row.get("name_cn", "").strip()
            if not name_cn:
                errors.append({"row": i, "error": "name_cn is required"})
                continue

            existing = await db.execute(select(Herb).where(Herb.name_cn == name_cn))
            if existing.scalar_one_or_none():
                errors.append({"row": i, "error": f"Duplicate: {name_cn}"})
                continue

            flavor_raw = row.get("flavor", "").strip()
            flavor = [f.strip() for f in flavor_raw.split("|") if f.strip()] if flavor_raw else None

            herb = Herb(
                name_cn=name_cn,
                name_pinyin=row.get("name_pinyin", "").strip() or None,
                category=row.get("category", "").strip() or "未分类",
                nature=row.get("nature", "").strip() or None,
                flavor=flavor,
                efficacy=row.get("efficacy", "").strip() or None,
            )
            db.add(herb)
            success_count += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})

    await db.commit()
    return {"success_count": success_count, "error_count": len(errors), "errors": errors}
