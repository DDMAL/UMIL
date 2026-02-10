"""Centralized error codes and messages for instrument operations."""

from typing import Dict


class ErrorCode:
    """
    Error codes for instrument-related operations.

    These codes provide consistent identifiers for different error scenarios
    and are included in API responses for client-side error handling.
    """

    # Validation errors (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_DATA = "MISSING_REQUIRED_DATA"
    INVALID_LANGUAGE_CODE = "INVALID_LANGUAGE_CODE"
    INVALID_HBS_CLASSIFICATION = "INVALID_HBS_CLASSIFICATION"
    INVALID_IMAGE_TYPE = "INVALID_IMAGE_TYPE"
    INVALID_IMAGE_SIZE = "INVALID_IMAGE_SIZE"
    FIELD_TOO_LONG = "FIELD_TOO_LONG"
    INVALID_JSON_FORMAT = "INVALID_JSON_FORMAT"

    # Duplicate detection errors (400)
    DUPLICATE_NAME_IN_REQUEST = "DUPLICATE_NAME_IN_REQUEST"
    DUPLICATE_NAME_IN_DATABASE = "DUPLICATE_NAME_IN_DATABASE"

    # Server errors (500)
    DATABASE_ERROR = "DATABASE_ERROR"
    INDEXING_ERROR = "INDEXING_ERROR"
    IMAGE_PROCESSING_ERROR = "IMAGE_PROCESSING_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # Rate limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Not found (404)
    INSTRUMENT_NOT_FOUND = "INSTRUMENT_NOT_FOUND"
    NAME_NOT_FOUND = "NAME_NOT_FOUND"

    # Permission errors (403)
    PERMISSION_DENIED = "PERMISSION_DENIED"


# User-facing error messages (safe to show to clients)
ERROR_MESSAGES: Dict[str, str] = {
    ErrorCode.VALIDATION_ERROR: "The submitted data is invalid. Please check your inputs and try again.",
    ErrorCode.MISSING_REQUIRED_DATA: "Required data is missing. Please fill in all required fields.",
    ErrorCode.INVALID_LANGUAGE_CODE: "One or more language codes are invalid.",
    ErrorCode.INVALID_HBS_CLASSIFICATION: "Valid Hornbostel-Sachs classification (at least 2 digits) is required.",
    ErrorCode.INVALID_IMAGE_TYPE: "Invalid image type. Allowed types: JPEG, PNG, GIF, WebP.",
    ErrorCode.INVALID_IMAGE_SIZE: "Image file size must be less than 5MB.",
    ErrorCode.FIELD_TOO_LONG: "One or more fields exceed the maximum allowed length.",
    ErrorCode.INVALID_JSON_FORMAT: "Invalid data format. Please check your request and try again.",
    ErrorCode.DUPLICATE_NAME_IN_REQUEST: "Duplicate entries detected in your submission.",
    ErrorCode.DUPLICATE_NAME_IN_DATABASE: "An instrument with this name already exists.",
    ErrorCode.DATABASE_ERROR: "A database error occurred. Please try again later.",
    ErrorCode.INDEXING_ERROR: "The instrument was created but search indexing failed. It will be indexed automatically.",
    ErrorCode.IMAGE_PROCESSING_ERROR: "An error occurred while processing the image.",
    ErrorCode.INTERNAL_ERROR: "An internal server error occurred. Please try again later.",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded. You can create up to 10 instruments per hour. Please try again later.",
    ErrorCode.INSTRUMENT_NOT_FOUND: "The requested instrument does not exist.",
    ErrorCode.NAME_NOT_FOUND: "The requested instrument name does not exist.",
    ErrorCode.PERMISSION_DENIED: "You do not have permission to perform this action.",
}


def get_error_message(error_code: str, **kwargs) -> str:
    """
    Get user-friendly error message for a given error code.

    Args:
        error_code: Error code from ErrorCode class
        **kwargs: Optional parameters for message formatting

    Returns:
        User-friendly error message
    """
    message = ERROR_MESSAGES.get(error_code, ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR])

    # Allow dynamic message formatting
    if kwargs:
        try:
            return message.format(**kwargs)
        except KeyError:
            return message

    return message
