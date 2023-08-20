import datetime
import typing
from decimal import Decimal
import io
import pytest

if typing.TYPE_CHECKING:
    from agnostic.pytest import agnostic


def test_progress_log(agnostic):
    """Add few entries to test run progress log
    """
    agnostic.test_run_heartbeat()
    agnostic.debug('Debug entry')
    agnostic.info('Info entry')
    agnostic.warning('Warning entry')
    agnostic.error('Error entry')
    agnostic.add_metric_over_time(
        'compute-consumption',
        {
            'cpu_percent': 20,
            'cpu_percent_process': 15.3,
            'ram_percent': 22
        }
    )
    assert True


@pytest.mark.xfail(reason='This might fail or might not')
def test_test_run_log(agnostic):
    """Add 2 test run logs with different markers
    """
    agnostic.set_log_marker('marker-1')
    agnostic.add_test_run_log(
        'Log for marker #1',
        'Just some fake log entry\nAnd some more text',
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
    )
    agnostic.set_log_marker('marker-2')
    log = agnostic.add_test_run_log(
        'Log for marker #2',
        'Lorem ipsum dolor\nUt quisquam amet amet',
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
    )
    agnostic.append_test_run_log(log, 'This goes after lorem ipsum\n ...')
    agnostic.append_test_run_log(log, 'And some lorem again\nLorem ipsum dolor')
    agnostic.add_metric_over_time(
        'compute-consumption',
        {
            'cpu_percent': 25.6,
            'cpu_percent_process': 17.7,
            'ram_percent': 24.5
        }
    )
    assert True


def test_test_run_metrics(agnostic):
    agnostic.add_test_run_metric(
        'metric.x', 42, 'The ultimate answer to your questions is "{:n}"'
    )
    agnostic.add_test_run_metric('metric.y', 33.212134, 'Some random number here {:2f}')
    agnostic.add_test_run_metric('metric.z', Decimal(2.3673299656712987), 'Decimal here {}')
    agnostic.add_metric_over_time(
        'compute-consumption',
        {
            'cpu_percent': 25.3,
            'cpu_percent_process': 17.2,
            'ram_percent': 24.2
        }
    )


def test_test_run_properties(agnostic):
    agnostic.set_test_run_property('environment', {'test-bench': {'revision': '0.7b'}})
    agnostic.set_test_run_property('firmware', {'updated-from': '1.3.57'})
    agnostic.set_test_run_property(
        'deployment', {'paths': {'tmp': '/tmp', '~': '/home/agnostic', 'config': '/etc/config'}}
    )
    agnostic.add_metric_over_time(
        'compute-consumption',
        {
            'cpu_percent': 25.1,
            'cpu_percent_process': 16.8,
            'ram_percent': 23.3
        }
    )


def test_fail(agnostic):
    """That's another description"""
    agnostic.add_metric_over_time(
        'compute-consumption',
        {
            'cpu_percent': 25.1,
            'cpu_percent_process': 16.8,
            'ram_percent': 23.3
        }
    )
    assert False


@pytest.mark.xfail(reason='This one always fails, but we pretend it is not')
def test_xfail(agnostic):
    """This test fails and demonstrates how xfail works
    """
    agnostic.add_metric_over_time(
        'compute-consumption',
        {
            'cpu_percent': 25.6,
            'cpu_percent_process': 16.9,
            'ram_percent': 23.1
        }
    )
    assert False


@pytest.mark.skip(reason='Just skip and forget')
def test_skip(agnostic):
    """Who even cares?
    """
    agnostic.add_metric_over_time(
        'compute-consumption',
        {
            'cpu_percent': 25.2,
            'cpu_percent_process': 16.7,
            'ram_percent': 23.5
        }
    )


def test_test_details(agnostic):
    with open(__file__, 'rb') as f:
        agnostic.add_test_attachment(
            f, 'test-attach-bin.txt', mime_type='text/plain'
        )
    with open(__file__, 'r') as f:
        agnostic.add_test_attachment(
            f, 'test-attach-str.txt', mime_type='text/plain'
        )
    agnostic.add_test_attachment(__file__)
    agnostic.add_test_attachment(
        io.BytesIO(b'BytesIO string'), 'from-bytesio.txt', mime_type='text/plain'
    )
    agnostic.add_test_attachment(
        io.StringIO('StringIO string'), 'from-bytesio.txt', mime_type='text/plain'
    )

    agnostic.add_test_metric('some.test.metric', 34.552, 'Just a metric {:1f}')
    agnostic.add_test_log(
        'Service A',
        'Lorem ipsum dolor',
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow() + datetime.timedelta(seconds=15)
    )
    agnostic.add_test_log(
        'Service b',
        'Lorem ipsum dolor\nAnd some more',
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow() + datetime.timedelta(seconds=35)
    )
    agnostic.test_run_heartbeat()
    agnostic.add_test_request(
        agnostic.RequestHTTP(
            method='GET',
            url='https://example.com',
            elapsed=0.03,
            response='<html>Example Web Site</html>'
        )
    )

    agnostic.add_test_request(
        agnostic.RequestSQL(
            query='select * from projects;',
            result='|project one| false |\n|project two| true |',
            elapsed=1.2
        )
    )

    agnostic.add_test_request(
        agnostic.RequestGRPC(
            method='GetProjects',
            request='*',
            response='project 1, project 2'
        )
    )

    agnostic.add_request(
        agnostic.RequestNATS(
            method='Pub',
            subject='projects.details',
            payload='*'
        )
    )
