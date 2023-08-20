import pytest


def pytest_configure(config):
    config.option.agnostic_url = 'http://localhost:8000/api/v1'
    config.option.agnostic_project_id = '4c984032-c8dd-49cf-99e6-7d1ca9ee656e'
    config.option.agnostic_sut_branch = 'master'
    config.option.agnostic_sut_version = '1.0.1'
    config.option.agnostic_test_branch = 'master'
    config.option.agnostic_test_version = '2.22-a'
    config.option.agnostic_variant = ['OS=Ubuntu 22', 'architecture=arm64']
    config.option.agnostic_offline = False


@pytest.fixture(scope='function')
def before():
    print('everything')
