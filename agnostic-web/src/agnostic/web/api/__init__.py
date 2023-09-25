import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette import concurrency

from agnostic.core import config
from agnostic.core.migrations import upgrade
from .routers_v1 import projects, test_runs, tests, logs, metrics, \
    progress, requests, metrics_ot, attachments, reporting, system
from .utils import SPA, simplify_operation_ids

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

api_v1 = FastAPI(ptitle='Agnostic Report', default_response_class=ORJSONResponse)
api_v1.include_router(projects.router)
api_v1.include_router(test_runs.router)
api_v1.include_router(tests.router)
api_v1.include_router(logs.router)
api_v1.include_router(metrics.router)
api_v1.include_router(metrics_ot.router)
api_v1.include_router(progress.router)
api_v1.include_router(requests.router)
api_v1.include_router(attachments.router)
api_v1.include_router(reporting.router)
api_v1.include_router(system.router)

simplify_operation_ids(api_v1)

app = FastAPI(title='Agnostic Report', version='1.0')
app.mount('/api/v1', api_v1)
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
