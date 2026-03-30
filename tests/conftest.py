import pytest
import os

# Устанавливаем TESTING=1 до всех импортов
os.environ['TESTING'] = '1'

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    close_all_sessions,
)
from sqlalchemy.pool import NullPool

from src.app import app
import src.database  # Импортируем модуль базы целиком
from src.repositories.models import Base
from src.config import settings
from src.repositories.models import ParcelType


@pytest.fixture(scope='session')
async def engine():
    test_db_url = settings.database_url.replace(
        settings.DB_NAME, f'{settings.DB_NAME}_test'
    )
    # Используем NullPool, чтобы соединения не зависали
    engine = create_async_engine(test_db_url, poolclass=NullPool)

    # ПОДМЕНЯЕМ глобальный session_maker в модуле database.py
    # Теперь и tasks.py, и depends.py будут использовать этот тестовый движок
    src.database.async_session_maker = async_sessionmaker(
        engine, expire_on_commit=False
    )

    yield engine
    await engine.dispose()


@pytest.fixture(scope='session', autouse=True)
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with src.database.async_session_maker() as session:
        session.add_all(
            [
                ParcelType(id=1, name='одежда'),
                ParcelType(id=2, name='электроника'),
                ParcelType(id=3, name='разное'),
            ]
        )
        await session.commit()
    yield
    await close_all_sessions()


@pytest.fixture
async def ac():
    # Больше не нужно переопределять get_session вручную через dependency_overrides,
    # так как мы подменили сам session_maker глобально.
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        yield client
