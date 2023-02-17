

class DALException(Exception):
    ...


class DuplicateError(DALException):
    ...


class NotFoundError(DALException):
    ...


class ForeignKeyError(DALException):
    ...


class InvalidArgumentsError(DALException):
    ...
