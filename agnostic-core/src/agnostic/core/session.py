from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from agnostic.core import config

engine = create_async_engine(
    f'{config.db_dialect}://{config.db_username}:{config.db_password}@'
    f'{config.db_host}:{config.db_port}/{config.db_database}',
    echo=not config.production,
    future=True
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
