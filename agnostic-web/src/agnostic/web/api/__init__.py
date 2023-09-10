import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette import concurrency

from agnostic.core import config
from agnostic.core.migrations import upgrade
from .routers import projects, test_runs, tests, logs, metrics, \
    progress, requests, metrics_ot, attachments, reporting, system
from .utils import SPA

base_dir = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

api = FastAPI(ptitle='Agnostic Report', default_response_class=ORJSONResponse)
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
app.mount('/api/v1', api)
app.mount('/', SPA(directory=base_dir / '..' / 'ui', html=True), name='ui')


@app.on_event('startup')
async def startup():
    log.info(
        f'Connecting to the "{config.options.db_database}" database '
        f'at {config.options.db_host}:{config.options.db_port}'
    )
    log.info('Migrating Agnostic database')
    await concurrency.run_in_threadpool(upgrade.run)
    log.info('Agnostic database migration finished')
