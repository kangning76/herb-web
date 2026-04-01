import os
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.herb import Herb  # noqa: F401
from app.models.user import User
from app.services.auth_service import hash_password, create_access_token

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/herbdb_test",
)


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create engine once per session, inside the session event loop."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture()
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Per-test DB session using nested transactions (savepoints) for isolation.

    The endpoint code calls session.commit(), which only commits the savepoint.
    After the test, the outer transaction is rolled back, undoing everything.
    """
    async with engine.connect() as conn:
        trans = await conn.begin()
        nested = await conn.begin_nested()

        session = AsyncSession(bind=conn, expire_on_commit=False)

        # When the application code calls session.commit() and the savepoint ends,
        # automatically start a new savepoint so subsequent operations work.
        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(session_sync, transaction):
            if transaction.nested and not transaction._parent.nested:
                session_sync.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            if nested.is_active:
                await nested.rollback()
            await trans.rollback()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client with DB override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user in the test DB."""
    user = User(username="testadmin", hashed_password=hash_password("testpass123"))
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture()
async def admin_token(admin_user: User) -> str:
    """JWT access token for the admin user."""
    return create_access_token(admin_user.username)


@pytest_asyncio.fixture()
async def auth_client(client: AsyncClient, admin_token: str) -> AsyncClient:
    """HTTP client with admin auth header pre-set."""
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client


@pytest_asyncio.fixture()
async def sample_herb(db_session: AsyncSession) -> Herb:
    """A single herb fixture for tests that need existing data."""
    herb = Herb(
        name_cn="黄芪",
        name_pinyin="Huang Qi",
        category="补气药",
        nature="温",
        flavor=["甘"],
        efficacy="补气升阳，固表止汗",
    )
    db_session.add(herb)
    await db_session.flush()
    return herb


@pytest_asyncio.fixture()
async def multiple_herbs(db_session: AsyncSession) -> list[Herb]:
    """Several herbs for search/filter/stats tests."""
    herbs_data = [
        {"name_cn": "黄芪", "name_pinyin": "Huang Qi", "category": "补气药", "nature": "温", "flavor": ["甘"], "efficacy": "补气升阳"},
        {"name_cn": "人参", "name_pinyin": "Ren Shen", "category": "补气药", "nature": "平", "flavor": ["甘", "苦"], "efficacy": "大补元气"},
        {"name_cn": "金银花", "name_pinyin": "Jin Yin Hua", "category": "清热药", "nature": "寒", "flavor": ["甘"], "efficacy": "清热解毒"},
        {"name_cn": "黄连", "name_pinyin": "Huang Lian", "category": "清热药", "nature": "寒", "flavor": ["苦"], "efficacy": "清热燥湿"},
        {"name_cn": "当归", "name_pinyin": "Dang Gui", "category": "补血药", "nature": "温", "flavor": ["甘", "辛"], "efficacy": "补血活血"},
    ]
    herbs = [Herb(**d) for d in herbs_data]
    db_session.add_all(herbs)
    await db_session.flush()
    return herbs
