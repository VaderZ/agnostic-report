from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from agnostic.core import config

engine = create_async_engine(
    f'{config.options.db_dialect}://{config.options.db_username}:{config.options.db_password}@'
    f'{config.options.db_host}:{config.options.db_port}/{config.options.db_database}',
    echo=not config.options.production,
    future=True
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
