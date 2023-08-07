from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from agnostic.core import config

engine = create_async_engine(
    f'{config.db_dialect}://{config.db_username}:{config.db_password}@'
    f'{config.db_host}:{config.db_port}/{config.db_database}',
    echo=not config.production,
    future=True
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
