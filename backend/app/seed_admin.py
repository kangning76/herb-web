"""Seed initial admin user."""
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.services.auth_service import hash_password


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.username == settings.ADMIN_USERNAME))
        if result.scalar_one_or_none():
            print(f"Admin user '{settings.ADMIN_USERNAME}' already exists.")
            return
        user = User(
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
        )
        session.add(user)
        await session.commit()
        print(f"Admin user '{settings.ADMIN_USERNAME}' created successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
