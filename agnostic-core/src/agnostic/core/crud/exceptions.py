class CRUDException(Exception):
    ...


class DuplicateError(CRUDException):
    ...


class NotFoundError(CRUDException):
    ...


class ForeignKeyError(CRUDException):
    ...


class InvalidArgumentsError(CRUDException):
    ...
