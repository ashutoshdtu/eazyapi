"""Exceptions raised by eazyapi."""


class DatabaseConnectionError(Exception):
    """Raised when there are issues connecting to the database."""

    pass


class RecordNotFoundError(Exception):
    """Raised when a record is not found in the database."""

    pass


class MultipleRecordsFoundError(Exception):
    """Raised when multiple records are found for a query when only one record was expected."""

    pass


class InvalidQueryError(Exception):
    """Raised when a query is not formed correctly."""

    pass


class DatabaseOperationError(Exception):
    """Raised when a database operation fails."""

    pass


class ValidationError(Exception):
    """Raised when the data provided to a method doesn't match the expected format."""

    pass
