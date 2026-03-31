from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HerbBase(BaseModel):
    name_cn: str = Field(..., max_length=100)
    name_pinyin: str | None = Field(None, max_length=200)
    category: str = Field(..., max_length=50)
    nature: str | None = Field(None, max_length=20)
    flavor: list[str] | None = None
    efficacy: str | None = None


class HerbCreate(HerbBase):
    pass


class HerbUpdate(BaseModel):
    name_cn: str | None = Field(None, max_length=100)
    name_pinyin: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=50)
    nature: str | None = Field(None, max_length=20)
    flavor: list[str] | None = None
    efficacy: str | None = None


class HerbResponse(HerbBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime


class HerbListResponse(BaseModel):
    items: list[HerbResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
