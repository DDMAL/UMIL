"""Validation utilities for instrument creation and management.

This module provides reusable validation functions for:
1. InstrumentName objects before bulk_create
2. Instrument metadata (HBS classification)
3. Uploaded image files

WHY EXPLICIT VALIDATION:
Django's bulk_create() method bypasses the normal model validation pipeline for performance
(1 database query instead of N queries). While this is great for performance, it means:
- full_clean() is never called
- Model.clean() methods don't run
- Django signals (pre_save, post_save) are not triggered
- Field validators still run at the database level, but errors are less clear

This module provides explicit pre-validation to:
1. Catch validation errors before hitting the database
2. Provide clear, contextual error messages
3. Future-proof against custom validation/signals added later
4. Enable reuse across views and management commands
"""

import re
from django.core.exceptions import ValidationError
from django.conf import settings
from typing import List, Tuple


def validate_instrument_names(instrument_names: List["InstrumentName"]) -> None:
    """
    Validate a list of InstrumentName objects before bulk creation.

    This function runs full_clean() on each object to catch:
    - Field-level validation (max_length, required fields, choices)
    - Model-level validation (custom clean() methods if added in the future)
    - Constraint validation (unique constraints, check constraints)

    IMPORTANT: This is REQUIRED when using bulk_create() because bulk_create()
    bypasses Django's validation system for performance.

    Args:
        instrument_names: List of unsaved InstrumentName instances

    Raises:
        ValidationError: If any object fails validation, with context about which
                        entry failed (entry #, name, language)

    Example:
        >>> names = [InstrumentName(name="Guitar", ...)]
        >>> validate_instrument_names(names)  # Raises ValidationError if invalid
        >>> InstrumentName.objects.bulk_create(names)  # Safe to bulk create
    """
    for idx, name_obj in enumerate(instrument_names):
        try:
            # full_clean() validates:
            # 1. Field constraints (max_length, choices, blank=False, etc.)
            # 2. Model.clean() method if it exists
            # 3. Unique constraints (at application level, not DB level)
            name_obj.full_clean()
        except ValidationError as e:
            # Enhance error message with context for better debugging
            language_code = (
                name_obj.language.wikidata_code if name_obj.language else "unknown"
            )
            raise ValidationError(
                f"Validation failed for entry #{idx + 1} "
                f"(name='{name_obj.name}', language='{language_code}'): {e}"
            ) from e


def validate_umil_label_constraint(instrument_names: List["InstrumentName"]) -> None:
    """
    Validate that at most one umil_label=True per instrument-language pair.

    This mirrors the database constraint:
        UniqueConstraint(
            fields=["instrument", "language"],
            condition=Q(umil_label=True),
            name="unique_umil_label_per_instrument_language"
        )

    While the database constraint will ultimately enforce this, validating upfront:
    1. Provides better error messages to users
    2. Catches logic bugs in label assignment code
    3. Avoids transaction rollback overhead from DB constraint violations

    Args:
        instrument_names: List of InstrumentName instances to validate

    Raises:
        ValidationError: If multiple labels exist for the same instrument-language pair,
                        with details about which combinations have violations

    Example:
        >>> names = [
        ...     InstrumentName(instrument=inst, language=en, umil_label=True),
        ...     InstrumentName(instrument=inst, language=en, umil_label=True),  # Duplicate!
        ... ]
        >>> validate_umil_label_constraint(names)  # Raises ValidationError
    """
    # Track label counts: (instrument_pk, language_code) -> count
    label_counts = {}

    for name_obj in instrument_names:
        if name_obj.umil_label:
            # Build key from instrument PK and language code
            instrument_pk = name_obj.instrument.pk if name_obj.instrument else "unknown"
            language_code = (
                name_obj.language.wikidata_code if name_obj.language else "unknown"
            )
            key = (instrument_pk, language_code)

            # Increment count for this combination
            label_counts[key] = label_counts.get(key, 0) + 1

    # Find violations (where count > 1)
    violations = {k: v for k, v in label_counts.items() if v > 1}

    if violations:
        # Build detailed error message
        error_details = [
            f"Instrument {inst_pk}, Language {lang}: {count} labels"
            for (inst_pk, lang), count in violations.items()
        ]
        raise ValidationError(
            f"Multiple umil_label=True detected: {'; '.join(error_details)}. "
            f"Only one label is allowed per instrument-language combination."
        )


def validate_hbs_classification(hbs_class: str) -> bool:
    """
    Validate Hornbostel-Sachs classification format.

    Valid formats:
    - Two digits minimum (e.g., "11", "21")
    - With optional sub-classifications (e.g., "21.2", "311.121")
    - First digit must be 1-5, second digit 0-9

    Args:
        hbs_class: Hornbostel-Sachs classification string to validate

    Returns:
        True if valid format, False otherwise

    Example:
        >>> validate_hbs_classification("11")       # True
        >>> validate_hbs_classification("21.2")     # True
        >>> validate_hbs_classification("311.121")  # True
        >>> validate_hbs_classification("6")        # False (needs 2 digits)
        >>> validate_hbs_classification("11x")      # False (invalid format)
    """
    if not hbs_class:
        return False
    # Pattern: one digit (1-5), followed by another digit, optionally followed by more .digits
    pattern = r"^[1-5][0-9](\.[0-9]+)*$"
    return bool(re.match(pattern, hbs_class)) and len(hbs_class) >= 2


def validate_image_file(image_file) -> Tuple[bool, str]:
    """
    Validate uploaded image file for size and content type.

    Checks against settings:
    - MAX_IMAGE_SIZE: Maximum file size in bytes
    - ALLOWED_IMAGE_TYPES: List of allowed MIME types

    Args:
        image_file: Django UploadedFile object (from request.FILES)
                   Can be None or missing (returns valid with empty error)

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        - If valid: (True, "")
        - If invalid: (False, "error message")

    Example:
        >>> is_valid, error = validate_image_file(request.FILES.get("image"))
        >>> if not is_valid:
        ...     return error_response(error)
    """
    if not image_file:
        return True, ""

    # Check file size
    if image_file.size > settings.MAX_IMAGE_SIZE:
        return False, "Image file size must be less than 5MB"

    # Check content type
    content_type = image_file.content_type
    if content_type not in settings.ALLOWED_IMAGE_TYPES:
        return (
            False,
            f"Invalid image type. Allowed types: JPEG, PNG, GIF, WebP",
        )

    return True, ""
