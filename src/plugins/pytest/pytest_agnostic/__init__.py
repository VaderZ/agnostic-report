import pytest
from _pytest.config.argparsing import Parser
from ._version import __revision__, __version__
from .agnostic.client import get_client, Client, RedisContext, LocalContext, HTTPClient

# Use 2 instances of the client for a case when client was hooked with async HTTP client
_agnostic: Client | None = None
_agnostic_hooked: Client | None = None


def pytest_addoption(parser: Parser):
    group = parser.getgroup('agnostic')
    group.addoption('--agnostic_url', dest='agnostic_url',
                    default=None, help='Agnostic URL')
    group.addoption('--agnostic_project_id', dest='agnostic_project_id',
                    default=None, help='Agnostic Project ID')
    group.addoption('--agnostic_test_run_id', dest='agnostic_test_run_id',
                    default=None, help='Agnostic Test Run ID')
    group.addoption('--agnostic_sut_version', dest='agnostic_sut_version',
                    default=None, help='Agnostic SUT version')
    group.addoption('--agnostic_sut_branch', dest='agnostic_sut_branch',
                    default=None, help='Agnostic SUT branch')
    group.addoption('--agnostic_test_version', dest='agnostic_test_version',
                    default=None, help='Agnostic test version')
    group.addoption('--agnostic_test_branch', dest='agnostic_test_branch',
                    default=None, help='Agnostic test branch')
    group.addoption('--agnostic_variant', dest='agnostic_variant', action='append',
                    default=None, help='Agnostic variant')
    group.addoption('--agnostic_property', dest='agnostic_property', action='append',
                    default=None, help='Agnostic property')
    group.addoption('--agnostic_offline', dest='agnostic_offline',
                    default=False, help='Agnostic offline mode')
    group.addoption('--agnostic_redis_host', dest='agnostic_redis_host',
                    default=None, help='Redis instance host for shared context')
    group.addoption('--agnostic_redis_port', dest='agnostic_redis_port',
                    default=6379, help='Redis instance port for shared context')
    group.addoption('--agnostic_redis_db', dest='agnostic_redis_db',
                    default=0, help='Redis instance DB for shared context')
    group.addoption('--agnostic_http_client', dest='agnostic_http_client',
                    default=None, help='Agnostic HTTP client type. Cannot be set from CLI')


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    options = session.config.option
    if not options.agnostic_offline:
        if not options.agnostic_url or not options.agnostic_project_id:
            raise RuntimeError('Agnostic URL and Project ID must be provided')

    if options.agnostic_redis_host:
        ctx = RedisContext(
            host=options.agnostic_redis_host,
            port=options.agnostic_redis_port,
            db=options.agnostic_redis_db
        )
    else:
        ctx = LocalContext()

    ctx.base_url = options.agnostic_url
    ctx.project_id = options.agnostic_project_id
    ctx.test_run_id = options.agnostic_test_run_id
    ctx.offline = options.agnostic_offline

    global _agnostic
    _agnostic = get_client(ctx)

    variants = options.agnostic_variant
    if variants:
        variants = dict(var.split('=') for var in variants)

    properties = options.agnostic_property
    if properties:
        properties = dict(prop.split('=') for prop in properties)

    _agnostic.start_test_run(
        sut_version=options.agnostic_sut_version,
        sut_branch=options.agnostic_sut_branch,
        test_version=options.agnostic_test_version,
        test_branch=options.agnostic_test_branch,
        variant=variants,
        properties=properties
    )
    global _agnostic_hooked
    if options.agnostic_http_client:
        _agnostic_hooked = get_client(ctx, options.agnostic_http_client)
    else:
        _agnostic_hooked = _agnostic
    _agnostic.info(f'Agnostic Report initialized for test run {ctx.test_run_id}')


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    _agnostic.info(f'Agnostic Report finished test run {_agnostic.ctx.test_run_id}')
    _agnostic.finish_test_run()


@pytest.fixture(scope='session')
def agnostic() -> Client:
    return _agnostic_hooked


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    _agnostic_hooked.start_test(
        name=item.name,
        path=item.nodeid.split('::')[0],
        description=getattr(item.obj, '__doc__')
    )


# See https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'setup':
        if rep.skipped:
            try:
                reason = rep.longrepr[-1].split(': ')[-1]
                _agnostic_hooked.finish_test(_agnostic.TestResult.SKIPPED, reason=reason)
            except Exception:
                pass
        elif rep.failed:
            _agnostic_hooked.finish_test(_agnostic.TestResult.FAILED, error_message=rep.longreprtext)
    elif rep.when == 'call':
        if hasattr(rep, 'wasxfail'):
            if rep.passed:
                _agnostic_hooked.finish_test(_agnostic.TestResult.XPASSED, reason=rep.wasxfail)
            else:
                _agnostic_hooked.finish_test(_agnostic.TestResult.XFAILED, error_message=rep.longreprtext, reason=rep.wasxfail)
        elif rep.failed:
            _agnostic_hooked.finish_test(_agnostic.TestResult.FAILED, error_message=rep.longreprtext)
        else:
            _agnostic_hooked.finish_test(_agnostic.TestResult.PASSED)
    elif rep.when == 'teardown':
        if rep.failed:
            _agnostic_hooked.finish_test(_agnostic.TestResult.FAILED, error_message=rep.longreprtext)
