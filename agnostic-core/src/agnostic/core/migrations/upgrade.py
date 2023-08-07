from pathlib import Path

from alembic import command
from alembic.config import Config

base_dir = Path(__file__).parent

alembic_config = Config(str(base_dir / 'alembic.ini'), )
alembic_config.set_section_option('alembic', 'script_location', str(base_dir))
alembic_config.set_section_option('alembic', 'prepend_sys_path', str(base_dir))


def run():
    command.upgrade(alembic_config, 'head')
