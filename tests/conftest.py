import pytest
import pytest_asyncio

from src._core.infrastructure.database.config import DatabaseConfig
from src._core.infrastructure.database.database import Base, Database


@pytest_asyncio.fixture(scope="session")
async def test_db():
    config = DatabaseConfig(echo=False)
    db = Database(
        database_engine="sqlite",
        database_user="",
        database_password="",
        database_host="",
        database_port=0,
        database_name=":memory:",
        config=config,
    )
    async with db.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield db
    await db.dispose()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
