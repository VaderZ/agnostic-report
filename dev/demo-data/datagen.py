import asyncio
import datetime
import itertools
import json
import mimetypes
import platform
import random
import sys
import uuid
from pathlib import Path

import lorem
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

base_folder = Path(__file__).parent
sys.path.insert(0, str(base_folder.parent.parent))

from agnostic_report.db.models import Project, TestRun, Test, TestRunVariant, Log, Progress, \
    Metric, MetricOverTime, Attachment, Request

postgres_url = None
engine = None
session = None


async def get_sessions(future):
    async with session() as s:
        return await future(s)


async def drop_all(session: AsyncSession):
    await session.execute(text("drop schema public cascade"))
    await session.execute(text('create schema public'))
    await session.commit()


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def migrate_schema():
    async with engine.begin() as conn:
        alembic_config = Config('./alembic.ini')
        alembic_config.set_section_option('alembic', 'sqlalchemy.url', postgres_url)
        await conn.run_sync(run_upgrade, Config('./alembic.ini'))


def create_projects(count: int):
    base = base_folder / 'resources' / 'configs'
    names = itertools.cycle(('Rich Configuration Project', 'Minimal Configuration Project'))

    async def _create_projects(session: AsyncSession):
        projects = []
        for i in range(count):
            name = next(names)
            with open(base / f'{name}.json') as f:
                projects.append(
                    Project(
                        name=f'{i + 1}. {name} ',
                        id=uuid.uuid4(),
                        config=json.load(f)
                    )
                )
        session.add_all(projects)
        await session.commit()
        return projects
    return _create_projects


def create_test_runs(projects: [Project], count: int):
    async def _create_test_runs(session: AsyncSession):
        test_runs = []
        test_run_variants = []
        for project in projects:
            for i in range(count):
                test_run_id = uuid.uuid4()
                start = datetime.datetime.utcnow() - datetime.timedelta(days=i + random.randint(0, 2))
                if i > 0 and i % 5 == 0:
                    finish = None
                    heartbeat = None
                else:
                    finish = start + datetime.timedelta(seconds=random.randint(500, 600))
                    heartbeat = finish - datetime.timedelta(seconds=random.randint(30, 60))
                sut_branch = random.choice(('main', 'john/fix-it', 'feature/smth-new'))
                test_branch = random.choice(('main', 'mary/flaky-fix', 'revert-model'))
                test_runs.append(TestRun(
                    id=test_run_id,
                    project_id=project.id,
                    start=start,
                    finish=finish,
                    heartbeat=heartbeat,
                    sut_branch=sut_branch,
                    sut_version=f'1.0.{i}',
                    test_branch=test_branch,
                    test_version=f'2.1.{i}',
                    properties={
                        'firmware': {
                            'updated-from': f'0.3.{25 + i}'
                        },
                        'environment': {
                            'test-bench': {
                                'revision': f'rev. 1.74.{random.randint(3, 5)}'
                            }
                        },
                        'deployment': {
                            'paths': {
                                'bin': '/opt/bin/app.run',
                                'logs': '/var/logs/app',
                                'store': '/var/lib/app/store',
                                'tmp': f'/tmp/{uuid.uuid4()}'
                            }
                        },
                        'tests': {
                            'config': {
                                'filters': {
                                    'slow': False,
                                    'smoke': True
                                },
                                'settings': {
                                    'max-retry': 3,
                                    'timeout': 90,
                                    'precompile': True
                                }
                            }
                        }
                    }
                ))
                test_run_variants.extend((
                    TestRunVariant(
                        test_run_id=test_run_id,
                        name='OS',
                        value=random.choice(('Linux', 'Windows'))
                    ),
                    TestRunVariant(
                        test_run_id=test_run_id,
                        name='architecture',
                        value=random.choice(('x86_64', 'arm64v8'))
                    )
                ))
        session.add_all(test_runs)
        session.add_all(test_run_variants)
        await session.commit()
        return test_runs
    return _create_test_runs


def create_tests(test_runs: [TestRun], test_count: int):

    def get_path():
        return f'tests/{random.choice(("api", "ui", "3rd-party"))}'

    def get_name():
        return random.choice((
            'buffer', 'port', 'image', 'sound', 'endpoint', 'schema', 'navigation', 'config',
            f'background_process[{random.choice(("collector", "reporter", "watchdog"))}]')
        )

    def get_result(tr_num, t_num):
        if tr_num > 0 and tr_num % 7 == 0:
            results = ('passed',)
            if t_num > 0:
                if t_num % 5 == 0:
                    results = ('failed',)
                elif t_num % 7 == 0:
                    results = ('passed', 'failed', 'skipped', 'xpassed', 'xfailed', None)
        else:
            if t_num > 0 and t_num % 7 == 0:
                results = ('passed', 'skipped', 'xpassed', 'xfailed')
            else:
                results = ('passed', )
        return random.choice(results)

    async def _create_tests(session: AsyncSession):
        tests = []
        for tr_num, test_run in enumerate(test_runs):
            for t_num in range(test_count):
                result = get_result(tr_num, t_num)
                tests.append(
                    Test(
                        test_run_id=test_run.id,
                        start=test_run.start + datetime.timedelta(seconds=15 * t_num),
                        finish=test_run.start + datetime.timedelta(seconds=15 * t_num + random.randint(7, 15)),
                        path=get_path(),
                        name=get_name(),
                        result=result,
                        reason=lorem.sentence() if result in ('skipped', 'xpassed', 'xfailed') else None,
                        error_message=lorem.sentence() if result in ('failed', 'xfailed') else None,
                        description=lorem.sentence()
                    )
                )
        session.add_all(tests)
        await session.commit()
        return tests
    return _create_tests


def make_log(min_lines=10, max_lines=200):
    log = ''
    offset = 0
    for i in range(min_lines, max_lines):
        offset += random.randint(50, 1000)
        log += f'{str(datetime.datetime.utcnow() + datetime.timedelta(milliseconds=offset)):30}' \
               f'{random.choice(("INFO", "DEBUG", "WARNING", "ERROR")):10}' \
               f'{lorem.sentence()}\n'
    return log


def create_test_run_logs(test_runs: [TestRun]):
    async def _create_test_run_logs(session: AsyncSession):
        logs = []
        for tr in test_runs:
            for log in ('mybin.exe.full', 'serial-console.pre-update', 'serial.post-update'):
                logs.append(
                    Log(
                        id=uuid.uuid4(),
                        test_run_id=tr.id,
                        name=log,
                        start=tr.start + datetime.timedelta(seconds=random.randint(0, 90)),
                        finish=tr.finish - datetime.timedelta(seconds=random.randint(0, 90)) if tr.finish else None,
                        body=make_log()
                    )
                )
        session.add_all(logs)
        await session.commit()
    return _create_test_run_logs


def create_test_logs(tests: [Test]):
    async def _create_test_logs(session: AsyncSession):
        logs = []
        for i, t in enumerate(tests):
            if i % 3 == 0:
                for log in ('mybin.exe.full', 'serial-console.pre-update', 'serial.post-update'):
                    logs.append(
                        Log(
                            id=uuid.uuid4(),
                            test_run_id=t.test_run_id,
                            test_id=t.id,
                            name=log,
                            start=t.start + datetime.timedelta(milliseconds=random.randint(0, 1500)),
                            finish=(t.finish - datetime.timedelta(milliseconds=random.randint(0, 1500))
                                    if t.finish else None),
                            body=make_log(min_lines=5, max_lines=20)
                        )
                    )
        session.add_all(logs)
        await session.commit()
    return _create_test_logs


def create_progress(tests: [Test]):
    async def _create_progress(session: AsyncSession):
        progress = []
        for i, t in enumerate(tests):
            test_id = None
            if i % 3 == 0:
                test_id = t.id
            progress.append(
                Progress(
                    id=uuid.uuid4(),
                    test_run_id=t.test_run_id,
                    test_id=test_id,
                    level=random.choice(('DEBUG', 'INFO', 'WARNING', 'ERROR')),
                    message=lorem.sentence(),
                    details=lorem.paragraph()
                )
            )
        session.add_all(progress)
        await session.commit()
    return _create_progress


def create_test_run_metrics(test_runs: [TestRun]):
    async def _create_test_run_metrics(session: AsyncSession):
        metrics = []
        for tr in test_runs:
            for m in (
                {
                    'name': 'firmware.time-to-apply-update',
                    'description': 'Time to apply update {:.2f}s',
                    'value': round(random.uniform(55, 85), 3)
                },
                {
                    'name': 'power.suspend.consumption',
                    'description': 'Device power consumption in suspend {:.2f}mW',
                    'value': round(random.uniform(1500, 2100), 2)
                },
                {
                    'name': 'compute.parallel-workers',
                    'description': 'Parallel workers in current session {:n}',
                    'value': random.randint(4, 8)
                }
            ):
                metrics.append(
                    Metric(
                        id=uuid.uuid4(),
                        test_run_id=tr.id,
                        timestamp=tr.start + datetime.timedelta(seconds=random.randint(5, 50)),
                        **m
                    )
                )
        session.add_all(metrics)
        await session.commit()
    return _create_test_run_metrics


def create_test_metrics(tests: [Test]):
    async def _create_test_metrics(session: AsyncSession):
        metrics = []
        for i, t in enumerate(tests):
            if i % 3 == 0:
                for m in (
                    {
                        'name': 'cache.hit-count',
                        'description': 'Cache hit {:n} times',
                        'value': random.randint(0, 5)
                    },
                    {
                        'name': 'cache.warm-up',
                        'description': 'Cache warm up took {:.2f}s',
                        'value': random.uniform(1, 3)
                    },
                ):
                    metrics.append(
                        Metric(
                            id=uuid.uuid4(),
                            test_id=t.id,
                            timestamp=t.start + datetime.timedelta(milliseconds=random.randint(1000, 5000)),
                            **m
                        )
                    )
        session.add_all(metrics)
        await session.commit()

    return _create_test_metrics


def create_metrics_ot(tests: [Test]):
    async def _create_metrics_ot(session: AsyncSession):
        base_seed = (10.1, 20.3, 20.8, 20.8, 21.2, 20.8, 31.4, 35.4, 37.1, 37, 36.8,
                     36.8, 27.5, 25.1, 22.9, 20.1, 19.8, 15.1, 10.5, 10.5, 10.5)
        process_cpu_seed = itertools.cycle(base_seed)
        cpu_seed = itertools.cycle([round(i * 1.2 + random.uniform(1, 3), 1) for i in base_seed])
        ram_seed = itertools.cycle([round(i * 1.4 + random.uniform(2, 7), 1) for i in base_seed])
        consumption_seed = itertools.cycle((19.5, 20.3, 20.8, 20.8, 21.2, 20.8, 21.4, 22.4, 22.1,
                                            23, 23.2, 23.5, 23.4, 23.5, 22.9, 20.1, 19.8, 20.5, 20.3, 19.4, 19.3))
        factor_seed = itertools.cycle((0.71, 0.71, 0.70, 0.70, 0.70, 0.69, 0.69, 0.68, 0.68, 0.68,
                                       0.67, 0.67, 0.67, 0.67, 0.68, 0.69, 0.68, 0.68, 0.69, 0.70, 0.70))
        metrics = []
        for t in tests:
            for i in range(5):
                metrics.append(
                    MetricOverTime(
                        id=uuid.uuid4(),
                        test_run_id=t.test_run_id,
                        test_id=t.id,
                        name='compute-consumption',
                        timestamp=t.start + datetime.timedelta(seconds=i),
                        values={
                            'cpu_percent': next(cpu_seed),
                            'ram_percent': next(ram_seed),
                            'cpu_percent_process': next(process_cpu_seed)
                        }
                    )
                )
                metrics.append(
                    MetricOverTime(
                        id=uuid.uuid4(),
                        test_run_id=t.test_run_id,
                        test_id=t.id,
                        name='power-consumption',
                        timestamp=t.start + datetime.timedelta(seconds=i),
                        values={
                            'power_consumption': next(consumption_seed),
                            'power_factor': next(factor_seed)
                        }
                    )
                )
        session.add_all(metrics)
        await session.commit()
    return _create_metrics_ot


def create_attachments(tests: [Test]):
    async def _create_attachments(session: AsyncSession):
        attachments = []
        base = base_folder / 'resources'
        contents = []
        for name in ('beep.wav', 'hello.py', 'sample.pdf', 'screenshot.png'):
            path = base / name
            with open(base / name, 'rb') as f:
                content = f.read()
                contents.append(
                    {'mime_type': mimetypes.guess_type(path)[0], 'name': name, 'content': content, 'size': len(content)}
                )
        for i, t in enumerate(tests):
            if i % 3 == 0:
                for c in contents[0:2]:
                    attachments.append(
                        Attachment(
                            id=uuid.uuid4(),
                            test_run_id=t.test_run_id,
                            test_id=t.id,
                            timestamp=t.start + datetime.timedelta(seconds=random.randint(1, 5)),
                            **c
                        )
                    )
            if i % 5 == 0:
                for c in contents[-2:]:
                    attachments.append(
                        Attachment(
                            id=uuid.uuid4(),
                            test_run_id=t.test_run_id,
                            test_id=t.id,
                            timestamp=t.start + datetime.timedelta(seconds=random.randint(1, 5)),
                            **c
                        )
                    )
        session.add_all(attachments)
        await session.commit()
    return _create_attachments


def create_requests(tests: [Test]):
    async def _create_requests(session: AsyncSession):
        requests = []
        for i, t in enumerate(tests):
            if i % 3 == 0:
                requests.append(
                    Request(
                        id=uuid.uuid4(),
                        test_run_id=t.test_run_id,
                        test_id=t.id,
                        timestamp=t.start + datetime.timedelta(milliseconds=random.randint(1000, 5000)),
                        request_type='http',
                        contents={
                            'code': 200,
                            'method': 'GET',
                            'url': 'https://example.com',
                            'elapsed': random.uniform(0.2, 3),
                            'response': '<h1>example.com</h1>'
                        }

                    )
                )
                requests.append(
                    Request(
                        id=uuid.uuid4(),
                        test_run_id=t.test_run_id,
                        test_id=t.id,
                        timestamp=t.start + datetime.timedelta(milliseconds=random.randint(1000, 5000)),
                        request_type='http',
                        contents={
                            'code': 500,
                            'method': 'POST',
                            'url': 'https://example.com/post',
                            'payload': '{"some_form_data": "smth"}',
                            'elapsed': random.uniform(0.2, 3),
                            'response': '500 SERVER ERROR'
                        }
                    )
                )
                requests.append(
                    Request(
                        id=uuid.uuid4(),
                        test_run_id=t.test_run_id,
                        test_id=t.id,
                        timestamp=t.start + datetime.timedelta(milliseconds=random.randint(1000, 5000)),
                        request_type='grpc',
                        contents={
                            'method': 'DoSomethingNice()',
                            'request': '{"howMuch": "twice"}',
                            'response': '{"didNice": true}',
                            'elapsed': random.uniform(0.2, 4)
                        }
                    )
                )
                requests.append(
                    Request(
                        id=uuid.uuid4(),
                        test_run_id=t.test_run_id,
                        test_id=t.id,
                        timestamp=t.start + datetime.timedelta(milliseconds=random.randint(1000, 5000)),
                        request_type='sql',
                        contents={
                            'query': 'select * from tests',
                            'result': '[\n  {"name": "test_one", "passed": true}, '
                                      '\n  {{"name": "test_two", "passed": false}}\n]',
                            'elapsed': random.uniform(0.2, 4)
                        }
                    )
                )
                requests.append(
                    Request(
                        id=uuid.uuid4(),
                        test_run_id=t.test_run_id,
                        test_id=t.id,
                        timestamp=t.start + datetime.timedelta(milliseconds=random.randint(1000, 5000)),
                        request_type='nats',
                        contents={
                            'method': 'Subscribe',
                            'subject': 'status.online',
                            'payload': '{"online": true}'
                        }
                    )
                )

        session.add_all(requests)
        await session.commit()

    return _create_requests


async def main(project_count, test_run_count, test_count):
    await get_sessions(drop_all)
    await migrate_schema()

    projects = await get_sessions(create_projects(project_count))
    test_runs = await get_sessions(create_test_runs(projects, test_run_count))
    tests = await get_sessions(create_tests(test_runs, test_count))
    await get_sessions(create_test_run_logs(test_runs))
    await get_sessions(create_test_logs(tests))
    await get_sessions(create_progress(tests))
    await get_sessions(create_test_run_metrics(test_runs))
    await get_sessions(create_test_metrics(tests))
    await get_sessions(create_metrics_ot(tests))
    await get_sessions(create_attachments(tests))
    await get_sessions(create_requests(tests))


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if len(sys.argv) > 1:
        postgres_url = sys.argv[1]
    else:
        postgres_url = 'postgresql+asyncpg://postgres:postgres@localhost:5432/agnostic'

    engine = create_async_engine(postgres_url, future=True)
    session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(2, 25, 25))
