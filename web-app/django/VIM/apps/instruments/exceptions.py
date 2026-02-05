"""Custom exceptions for instrument operations."""

from typing import Any, Dict, Optional


class InstrumentException(Exception):
    """
    Base exception for all instrument-related errors.

    Attributes:
        error_code: Machine-readable error code
        message: User-friendly error message
        status_code: HTTP status code to return
        details: Additional error details (only logged, never sent to client)
    """

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationException(InstrumentException):
    """Raised when validation fails (HTTP 400)."""

    def __init__(
        self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(error_code, message, status_code=400, details=details)


class DuplicateException(InstrumentException):
    """Raised when duplicate data is detected (HTTP 400)."""

    def __init__(
        self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(error_code, message, status_code=400, details=details)


class NotFoundException(InstrumentException):
    """Raised when a resource is not found (HTTP 404)."""

    def __init__(
        self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(error_code, message, status_code=404, details=details)


class PermissionException(InstrumentException):
    """Raised when user lacks permission (HTTP 403)."""

    def __init__(
        self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(error_code, message, status_code=403, details=details)


class DatabaseException(InstrumentException):
    """Raised when database operations fail (HTTP 500)."""

    def __init__(
        self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(error_code, message, status_code=500, details=details)
