"""Django view to handle user input to UMIl database"""

import json
import logging
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, JsonResponse
from django.core.exceptions import ValidationError
from VIM.apps.instruments.models import Instrument, Language, InstrumentName
from VIM.apps.instruments.utils.validators import (
    validate_instrument_names,
    validate_umil_label_constraint,
)
from VIM.apps.instruments.exceptions import (
    ValidationException,
    NotFoundException,
    PermissionException,
)
from VIM.apps.instruments.error_codes import ErrorCode, get_error_message
from VIM.apps.instruments.utils.response_helpers import (
    success_response,
    handle_exception,
)
from VIM.apps.instruments.utils.solr_indexer import index_single_instrument
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def add_name(request: HttpRequest, umil_id: str) -> JsonResponse:
    """
    View to add new instrument names to UMIL database.

    umil_id is received from the URL path parameter, not the request body.

    This view expects a POST request with the JSON body:
    {
        "entries": [
            {
                "language": "en",
                "name": "English label",
                "source": "Source name",
            },
            {
                "language": "fr",
                "name": "French label",
                ...
            }
        ],
    }

    Returns:
        JsonResponse: JSON response with status and message
    """
    try:
        # Parse the JSON request body
        try:
            data: Dict[str, Any] = json.loads(request.body)
        except json.JSONDecodeError:
            raise ValidationException(
                ErrorCode.INVALID_JSON_FORMAT,
                "Invalid JSON format",
                details={"field": "request_body"},
            )

        entries: List[Dict[str, str]] = data.get("entries", [])

        if not entries:
            raise ValidationException(
                ErrorCode.MISSING_REQUIRED_DATA,
                "Missing required data",
                details={"missing": ["entries"]},
            )

        # Fetch the instrument from the database
        try:
            instrument = Instrument.objects.get(umil_id=umil_id)
        except Instrument.DoesNotExist:
            raise NotFoundException(
                ErrorCode.INSTRUMENT_NOT_FOUND,
                f"Instrument with UMIL ID '{umil_id}' does not exist",
                details={"umil_id": umil_id},
            )

        # Extract unique language codes from entries to avoid loading all languages
        submitted_lang_codes = {entry["language"] for entry in entries}

        # Fetch only submitted unique languages
        language = {
            lang.wikidata_code: lang
            for lang in Language.objects.filter(wikidata_code__in=submitted_lang_codes)
        }

        # Validate all submitted language codes exist upfront
        invalid_codes = submitted_lang_codes - set(language.keys())
        if invalid_codes:
            raise ValidationException(
                ErrorCode.INVALID_LANGUAGE_CODE,
                f"Invalid language code(s): {', '.join(sorted(invalid_codes))}",
                details={"invalid_codes": list(invalid_codes)},
            )

        # considering entries with multiple of the same language, create a dictionary to track if a label has
        # been assigned to a previous entry
        entry_labels = {entry["language"]: False for entry in entries}

        instrument_names_to_create = []

        # Keep track of the (name, language_code) enteties for fast detection of duplication in the request
        unique_instruments = set()

        for entry in entries:
            language_code: str = entry["language"]
            name: str = entry["name"]
            source: str = entry["source"]

            # Validate that entry info is provided
            if not name or not source or not language_code:
                raise ValidationException(
                    ErrorCode.MISSING_REQUIRED_DATA,
                    "Missing entry information",
                    details={"entry": entry},
                )

            # Find language object from language code dictionary
            # Guaranteed to exist due to upfront validation
            language_obj: Language = language[language_code]

            # Skip the entry if duplicate in batch
            entry_key = (name.lower(), language_code)
            if entry_key in unique_instruments:
                continue
            unique_instruments.add(entry_key)

            # Check if the entry exists in UMIL_db
            if InstrumentName.objects.filter(
                instrument=instrument,
                language__wikidata_code=language_code,
                name__iexact=name,
            ).exists():
                continue

            # Within the entries, check if the language already has a name
            # if it does, set umil_label to False
            # otherwise, check against the UMILdb
            if entry_labels[language_code]:
                umil_label = False
            else:
                umil_label: bool = not (
                    instrument.instrumentname_set.filter(
                        language__wikidata_code=language_code
                    ).exists()
                )
                entry_labels[language_code] = (
                    True  # Mark that this language now has a name
                )

            # Prepare the InstrumentName object
            instrument_names_to_create.append(
                InstrumentName(
                    instrument=instrument,
                    language=language_obj,
                    name=name,
                    source_name=source,
                    umil_label=umil_label,
                    contributor=request.user,
                )
            )

        # Validate all InstrumentName objects before bulk creation
        # REQUIRED because bulk_create() bypasses Django validation for performance
        # See validators.py for detailed explanation
        try:
            validate_instrument_names(instrument_names_to_create)
            validate_umil_label_constraint(instrument_names_to_create)
        except ValidationError as ve:
            raise ValidationException(
                ErrorCode.VALIDATION_ERROR,
                get_error_message(ErrorCode.VALIDATION_ERROR),
                details={"validation_errors": str(ve)},
            )

        # Bulk create all InstrumentName objects
        InstrumentName.objects.bulk_create(instrument_names_to_create)

        # Schedule Solr reindex after commit so new names are searchable
        if instrument_names_to_create:

            def schedule_indexing():
                try:
                    index_success = index_single_instrument(instrument.pk)
                    if not index_success:
                        instrument.needs_reindexing = True
                        instrument.save(update_fields=["needs_reindexing"])
                        logger.warning(
                            f"Instrument {instrument.pk} (UMIL ID: {instrument.umil_id}) "
                            "names added but failed to reindex in Solr. "
                            "Marked for reindexing. Run 'python manage.py reindex_failed' to retry."
                        )
                except Exception as e:
                    instrument.needs_reindexing = True
                    instrument.save(update_fields=["needs_reindexing"])
                    logger.error(
                        f"Error reindexing instrument {instrument.pk} (UMIL ID: {instrument.umil_id}) "
                        "after adding names. Marked for reindexing.",
                        exc_info=True,
                    )

            transaction.on_commit(schedule_indexing)

        return success_response("All entries saved successfully")

    except Exception as e:
        return handle_exception(
            e,
            context="add_name",
            request_user=(
                request.user.username if request.user.is_authenticated else None
            ),
        )


def delete_name(request: HttpRequest) -> JsonResponse:
    """View to delete an instrument name from UMIL database."""
    try:
        # Parse the JSON request body
        try:
            data: Dict[str, Any] = json.loads(request.body)
        except json.JSONDecodeError:
            raise ValidationException(
                ErrorCode.INVALID_JSON_FORMAT,
                "Invalid JSON format",
                details={"field": "request_body"},
            )

        name_id: str = data.get("instrument_name_id")

        # Check if name_id is provided
        if not name_id:
            raise ValidationException(
                ErrorCode.MISSING_REQUIRED_DATA,
                "Missing required data",
                details={"missing": ["instrument_name_id"]},
            )

        # Fetch the instrument name
        try:
            instrument_name = InstrumentName.objects.get(id=name_id)
        except InstrumentName.DoesNotExist:
            raise NotFoundException(
                ErrorCode.NAME_NOT_FOUND,
                "The requested instrument name does not exist",
                details={"name_id": name_id},
            )

        # Check permissions
        if not (
            request.user.is_superuser or instrument_name.contributor == request.user
        ):
            raise PermissionException(
                ErrorCode.PERMISSION_DENIED,
                "You are not allowed to delete this name",
                details={
                    "name_id": name_id,
                    "contributor": (
                        instrument_name.contributor.username
                        if instrument_name.contributor
                        else None
                    ),
                },
            )

        instrument_id = instrument_name.instrument_id

        # Delete the name
        instrument_name.delete()

        # Schedule Solr reindex after commit so the deleted name is removed from search
        def schedule_indexing():
            try:
                index_success = index_single_instrument(instrument_id)
                if not index_success:
                    Instrument.objects.filter(pk=instrument_id).update(
                        needs_reindexing=True
                    )
                    logger.warning(
                        f"Instrument {instrument_id} name deleted but failed to reindex in Solr. "
                        "Marked for reindexing. Run 'python manage.py reindex_failed' to retry."
                    )
            except Exception as e:
                Instrument.objects.filter(pk=instrument_id).update(
                    needs_reindexing=True
                )
                logger.error(
                    f"Error reindexing instrument {instrument_id} after deleting name. "
                    "Marked for reindexing.",
                    exc_info=True,
                )

        transaction.on_commit(schedule_indexing)

        return success_response("Instrument name deleted successfully")

    except Exception as e:
        return handle_exception(
            e,
            context="delete_name",
            request_user=(
                request.user.username if request.user.is_authenticated else None
            ),
        )


@login_required
@require_http_methods(["POST", "DELETE"])
def update_umil_db(request: HttpRequest, umil_id: str) -> JsonResponse:
    if request.method == "POST":
        return add_name(request, umil_id)

    elif request.method == "DELETE":
        return delete_name(request)
