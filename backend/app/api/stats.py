from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import herb_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
async def overview(db: AsyncSession = Depends(get_db)):
    return await herb_service.get_overview(db)


@router.get("/category-distribution")
async def category_distribution(db: AsyncSession = Depends(get_db)):
    return await herb_service.get_category_distribution(db)


@router.get("/nature-distribution")
async def nature_distribution(db: AsyncSession = Depends(get_db)):
    return await herb_service.get_nature_distribution(db)


@router.get("/flavor-distribution")
async def flavor_distribution(db: AsyncSession = Depends(get_db)):
    return await herb_service.get_flavor_distribution(db)
