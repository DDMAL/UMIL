"""Helper functions for creating consistent JSON responses."""

import logging
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse

from VIM.apps.instruments.error_codes import ErrorCode, get_error_message
from VIM.apps.instruments.exceptions import InstrumentException

logger = logging.getLogger(__name__)


def success_response(message: str, status: int = 200, **extra_data) -> JsonResponse:
    """
    Create a success JSON response.

    Args:
        message: Success message
        status: HTTP status code (default 200)
        **extra_data: Additional data to include in response

    Returns:
        JsonResponse with success status

    Example:
        return success_response(
            "Instrument created successfully",
            status=201,
            instrument_id=123,
            umil_id="UMIL-00123"
        )
    """
    response_data = {"status": "success", "message": message, **extra_data}
    return JsonResponse(response_data, status=status)


def error_response(
    error_code: str,
    message: Optional[str] = None,
    status: int = 400,
    debug_info: Optional[str] = None,
    **extra_data,
) -> JsonResponse:
    """
    Create an error JSON response.

    Args:
        error_code: Error code from ErrorCode class
        message: Override default error message (optional)
        status: HTTP status code
        debug_info: Additional debug information (only included in DEBUG mode)
        **extra_data: Additional data to include in response

    Returns:
        JsonResponse with error status

    Example:
        return error_response(
            ErrorCode.VALIDATION_ERROR,
            status=400,
            debug_info=str(validation_exception)
        )
    """
    # Use provided message or default for error code
    user_message = message or get_error_message(error_code)

    response_data = {
        "status": "error",
        "message": user_message,
        "error_code": error_code,
        **extra_data,
    }

    # Include debug information only in development
    if settings.DEBUG and debug_info:
        response_data["debug_info"] = debug_info

    return JsonResponse(response_data, status=status)


def handle_exception(
    exception: Exception, context: str, request_user: Optional[str] = None
) -> JsonResponse:
    """
    Convert an exception to an appropriate JSON error response.

    This function:
    1. Logs the full exception details server-side
    2. Returns a safe, user-friendly error response
    3. Includes debug info only when DEBUG=True

    Args:
        exception: The exception to handle
        context: Context string for logging (e.g., "create_instrument")
        request_user: Username for logging (optional)

    Returns:
        JsonResponse with appropriate error message and status code

    Example:
        try:
            create_instrument_logic()
        except Exception as e:
            return handle_exception(e, "create_instrument", request.user.username)
    """
    # Handle our custom exceptions
    if isinstance(exception, InstrumentException):
        # Log with appropriate level based on status code
        log_level = logging.WARNING if exception.status_code < 500 else logging.ERROR

        logger.log(
            log_level,
            f"{context}: {exception.error_code} - {exception.message}",
            extra={
                "error_code": exception.error_code,
                "user": request_user or "anonymous",
                "details": exception.details,
            },
            exc_info=True if exception.status_code >= 500 else False,
        )

        return error_response(
            error_code=exception.error_code,
            message=exception.message,
            status=exception.status_code,
            debug_info=str(exception) if settings.DEBUG else None,
        )

    # Handle Django's ValidationError
    if isinstance(exception, ValidationError):
        logger.warning(
            f"{context}: Django ValidationError - {exception}",
            extra={"user": request_user or "anonymous"},
        )

        return error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            status=400,
            debug_info=str(exception) if settings.DEBUG else None,
        )

    # Handle unexpected exceptions
    logger.error(
        f"{context}: Unexpected error - {type(exception).__name__}: {exception}",
        extra={"user": request_user or "anonymous"},
        exc_info=True,  # Include full stack trace in logs
    )

    return error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        status=500,
        debug_info=(
            f"{type(exception).__name__}: {str(exception)}" if settings.DEBUG else None
        ),
    )


def handle_rate_limit_exceeded(
    request: HttpRequest, exception: Exception
) -> JsonResponse:
    """
    Global handler for django-ratelimit exceptions.
    Returns HTTP 429 (Too Many Requests) with a user-friendly error message.

    This function is configured as RATELIMIT_VIEW in settings.py and is called
    automatically by django-ratelimit when any rate-limited view exceeds its limit.

    Args:
        request: The HTTP request that was rate limited
        exception: The Ratelimited exception raised by django-ratelimit

    Returns:
        JsonResponse with 429 status code and rate limit error message

    Example:
        # In settings.py
        RATELIMIT_VIEW = "VIM.apps.instruments.utils.response_helpers.handle_rate_limit_exceeded"
    """
    logger.warning(
        f"Rate limit exceeded for {request.path}",
        extra={
            "user": (
                request.user.username if request.user.is_authenticated else "anonymous"
            ),
            "path": request.path,
            "method": request.method,
        },
    )

    return error_response(error_code=ErrorCode.RATE_LIMIT_EXCEEDED, status=429)
