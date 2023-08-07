import os

db_dialect: str = os.getenv('AGNOSTIC_DB_DIALECT', 'postgresql+asyncpg')
db_username: str = os.getenv('AGNOSTIC_DB_USERNAME', 'postgres')
db_password: str = os.getenv('AGNOSTIC_DB_PASSWORD', 'postgres')
db_host: str = os.getenv('AGNOSTIC_DB_HOST', 'localhost')
db_port: int = os.getenv('AGNOSTIC_DB_PORT', 5432)
db_database: str = os.getenv('AGNOSTIC_DB_NAME', 'agnostic')

web_host: str = os.getenv('AGNOSTIC_WEB_HOST', '0.0.0.0')
web_port: int = os.getenv('AGNOSTIC_WEB_PORT', 8000)

production: bool = os.getenv('AGNOSTIC_PRODUCTION', True)
