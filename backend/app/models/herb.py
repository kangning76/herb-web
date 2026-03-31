from datetime import datetime

from sqlalchemy import ARRAY, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Herb(Base):
    __tablename__ = "herbs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_cn: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name_pinyin: Mapped[str | None] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    nature: Mapped[str | None] = mapped_column(String(20))
    flavor: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    efficacy: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
