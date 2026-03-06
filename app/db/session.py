from typing import AsyncGenerator
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG, 
    pool_size=10,           # Persistent connections in pool
    max_overflow=20,        # Additional temporary connections
    pool_pre_ping=True,     # Critical: checks health before use to avoid stale errors
    future=True,
    connect_args={
        "server_settings": {
            "jit": "off"
        }
    }
)

AsyncSessionLocal = async_sessionmaker[AsyncSession](
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False, # Required for async to prevent attribute errors after commit
    autocommit=False, 
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()