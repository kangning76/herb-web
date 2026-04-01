import math
import os
import time

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.common import ImportResult, MessageResponse
from app.schemas.herb import HerbCreate, HerbListResponse, HerbResponse, HerbUpdate
from app.services import herb_service

router = APIRouter(prefix="/herbs", tags=["herbs"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


@router.get("", response_model=HerbListResponse)
async def list_herbs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    nature: str | None = None,
    q: str | None = None,
    sort_by: str = Query("created_at", pattern="^(name_cn|created_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await herb_service.get_herbs(
        db, page=page, page_size=page_size,
        category=category, nature=nature, q=q,
        sort_by=sort_by, order=order,
    )
    return HerbListResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/categories", response_model=list[str])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await herb_service.get_categories(db)


@router.get("/{herb_id}", response_model=HerbResponse)
async def get_herb(herb_id: int, db: AsyncSession = Depends(get_db)):
    herb = await herb_service.get_herb_by_id(db, herb_id)
    if not herb:
        raise HTTPException(status_code=404, detail="Herb not found")
    return herb


@router.post("", response_model=HerbResponse, status_code=201)
async def create_herb(
    data: HerbCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    try:
        return await herb_service.create_herb(db, data)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Herb with this name already exists")


@router.put("/{herb_id}", response_model=HerbResponse)
async def update_herb(
    herb_id: int,
    data: HerbUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    herb = await herb_service.get_herb_by_id(db, herb_id)
    if not herb:
        raise HTTPException(status_code=404, detail="Herb not found")
    return await herb_service.update_herb(db, herb, data)


@router.delete("/{herb_id}", response_model=MessageResponse)
async def delete_herb(
    herb_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    herb = await herb_service.get_herb_by_id(db, herb_id)
    if not herb:
        raise HTTPException(status_code=404, detail="Herb not found")
    await herb_service.delete_herb(db, herb)
    return MessageResponse(message="Herb deleted")


@router.post("/{herb_id}/image", response_model=HerbResponse)
async def upload_image(
    herb_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    herb = await herb_service.get_herb_by_id(db, herb_id)
    if not herb:
        raise HTTPException(status_code=404, detail="Herb not found")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP images are allowed")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 5MB")

    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{herb_id}_{int(time.time())}.{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, "herbs")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    herb.image_url = f"/uploads/herbs/{filename}"
    await db.commit()
    await db.refresh(herb)
    return herb


@router.post("/import", response_model=ImportResult)
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    content = (await file.read()).decode("utf-8-sig")
    result = await herb_service.import_herbs_from_csv(db, content)
    return ImportResult(**result)
