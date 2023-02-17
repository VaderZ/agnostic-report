import asyncio
import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from . import config
from .api.routers import projects, test_runs, tests, logs, metrics, \
    progress, requests, metrics_ot, attachments, reporting, system
from .api.utils import SPA

base_dir = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

api = APIRouter(prefix='/api/v1', default_response_class=ORJSONResponse)
api.include_router(projects.router)
api.include_router(test_runs.router)
api.include_router(tests.router)
api.include_router(logs.router)
api.include_router(metrics.router)
api.include_router(metrics_ot.router)
api.include_router(progress.router)
api.include_router(requests.router)
api.include_router(attachments.router)
api.include_router(reporting.router)
api.include_router(system.router)

app = FastAPI(title='Agnostic Report', version='1.0')
app.include_router(api)
app.mount('/', SPA(directory=base_dir / 'ui' / 'dist', html=True), name='ui')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def startup():
    log.info(f'Connecting to the "{config.db_database}" database at {config.db_host}:{config.db_port}')
    log.info('Migrating Agnostic database')
    alembic_config = Config(str(base_dir / 'alembic.ini'))
    alembic_config.set_section_option('alembic', 'script_location', str(base_dir / 'migrations'))
    alembic_config.set_section_option('alembic', 'prepend_sys_path', str(base_dir))
    await asyncio.get_event_loop().run_in_executor(
        None, lambda: command.upgrade(alembic_config, 'head')
    )
    log.info('Agnostic database migration finished')
