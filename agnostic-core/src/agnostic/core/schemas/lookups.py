__all__ = ['TestResult', 'Level', 'RequestType']
from enum import StrEnum


class TestResult(StrEnum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    XPASSED = 'xpassed'
    XFAILED = 'xfailed'


class Level(StrEnum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class RequestType(StrEnum):
    HTTP = 'http'
    GRPC = 'grpc'
    SQL = 'sql'
    NATS = 'nats'
