"""Django view to handle instrument creation by users."""

import json
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from django.conf import settings
from VIM.apps.instruments.models import Instrument, Language, InstrumentName, AVResource
from VIM.apps.instruments.utils.solr_indexer import index_single_instrument
from VIM.apps.instruments.utils.image_processor import process_uploaded_image
from VIM.apps.instruments.utils.validators import (
    validate_instrument_names,
    validate_umil_label_constraint,
    validate_hbs_classification,
    validate_image_file,
)
from VIM.apps.instruments.exceptions import (
    ValidationException,
    DuplicateException,
)
from VIM.apps.instruments.error_codes import ErrorCode, get_error_message
from VIM.apps.instruments.utils.response_helpers import (
    success_response,
    error_response,
    handle_exception,
)
from typing import Dict, List

logger = logging.getLogger(__name__)


class CreateInstrumentView(LoginRequiredMixin, TemplateView):
    """
    Displays the create instrument form.
    Requires authentication.
    """

    template_name = "instruments/create.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["languages"] = list(
            Language.objects.values(
                "wikidata_code",
                "autonym",
                "en_label",
                "html_direction",
            )
        )

        context["active_tab"] = "instruments"
        return context


@login_required
@ratelimit(key="user", rate=settings.CREATE_INSTRUMENT_RATE, method="POST", block=True)
@require_http_methods(["POST"])
def create_instrument(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to create a new instrument with names.
    Rate limited to 10 requests per hour per authenticated user.

    Expects multipart/form-data with:
    - entries: JSON string of name entries array
    - instrument_source: Overall source for the instrument
    - hornbostel_sachs_class: HBS classification
    - image: File upload (optional)
    - image_source: Image attribution (required if image provided)

    Returns:
        JsonResponse with created instrument ID or error message
    """
    try:
        # Parse entries from form data (JSON string)
        entries_json = request.POST.get("entries", "[]")
        try:
            entries: List[Dict[str, str]] = json.loads(entries_json)
        except json.JSONDecodeError:
            raise ValidationException(
                ErrorCode.INVALID_JSON_FORMAT,
                "Invalid entries format",
                details={"field": "entries"},
            )

        instrument_source: str = request.POST.get("instrument_source", "").strip()
        hbs_class: str = request.POST.get("hornbostel_sachs_class", "").strip()
        image_file = request.FILES.get("image")
        image_source: str = request.POST.get("image_source", "").strip()

        # Validation
        if not entries:
            raise ValidationException(
                ErrorCode.MISSING_REQUIRED_DATA,
                "At least one name entry is required",
                details={"field": "entries"},
            )

        if not instrument_source:
            raise ValidationException(
                ErrorCode.MISSING_REQUIRED_DATA,
                "Instrument source is required",
                details={"field": "instrument_source"},
            )

        # Validate instrument source length
        if len(instrument_source) > 255:
            raise ValidationException(
                ErrorCode.FIELD_TOO_LONG,
                "Instrument source must be 255 characters or less",
                details={"field": "instrument_source", "max_length": 255},
            )

        if not validate_hbs_classification(hbs_class):
            raise ValidationException(
                ErrorCode.INVALID_HBS_CLASSIFICATION,
                get_error_message(ErrorCode.INVALID_HBS_CLASSIFICATION),
                details={"field": "hornbostel_sachs_class", "value": hbs_class},
            )

        # Validate image fields
        if image_file:
            is_valid, error_msg = validate_image_file(image_file)
            if not is_valid:
                # Determine specific error code based on message
                if "size" in error_msg.lower():
                    error_code = ErrorCode.INVALID_IMAGE_SIZE
                else:
                    error_code = ErrorCode.INVALID_IMAGE_TYPE
                raise ValidationException(
                    error_code, error_msg, details={"field": "image"}
                )

            if not image_source:
                raise ValidationException(
                    ErrorCode.MISSING_REQUIRED_DATA,
                    "Image source is required when providing an image",
                    details={"field": "image_source"},
                )

            # Validate image source length
            if len(image_source) > 200:
                raise ValidationException(
                    ErrorCode.FIELD_TOO_LONG,
                    "Image source must be 200 characters or less",
                    details={"field": "image_source", "max_length": 200},
                )

        # Validate entries and check for language codes
        # Extract unique language codes from entries to avoid loading all languages
        # This optimization reduces database queries from 500+ rows to #unique-user-submitted rows
        submitted_lang_codes = {
            entry.get("language") for entry in entries if entry.get("language")
        }

        # Fetch only languages that are actually submitted
        language_codes = {
            lang.wikidata_code: lang
            for lang in Language.objects.filter(wikidata_code__in=submitted_lang_codes)
        }

        # Validate all submitted language codes exist upfront
        invalid_codes = submitted_lang_codes - set(language_codes.keys())
        if invalid_codes:
            raise ValidationException(
                ErrorCode.INVALID_LANGUAGE_CODE,
                f"Invalid language code(s): {', '.join(sorted(invalid_codes))}",
                details={"invalid_codes": list(invalid_codes)},
            )

        for entry in entries:
            if (
                not entry.get("language")
                or not entry.get("name")
                or not entry.get("source")
            ):
                raise ValidationException(
                    ErrorCode.MISSING_REQUIRED_DATA,
                    "Each entry requires language, name, and source",
                    details={"entry": entry},
                )
            # Language code validation already done above

        # Check for duplicates within the request (case-insensitive)
        seen_entries = set()
        for entry in entries:
            entry_key = (entry["name"].lower(), entry["language"])
            if entry_key in seen_entries:
                raise DuplicateException(
                    ErrorCode.DUPLICATE_NAME_IN_REQUEST,
                    f"Duplicate entry detected: '{entry['name']}' in language '{entry['language']}' appears multiple times in your submission",
                    details={"name": entry["name"], "language": entry["language"]},
                )
            seen_entries.add(entry_key)

        # Create instrument and names in a transaction
        with transaction.atomic():
            # Check for duplicates in existing database with row-level locking
            for entry in entries:
                if (
                    InstrumentName.objects.select_for_update()
                    .filter(
                        language__wikidata_code=entry["language"],
                        name__iexact=entry["name"],
                    )
                    .exists()
                ):
                    raise DuplicateException(
                        ErrorCode.DUPLICATE_NAME_IN_DATABASE,
                        f"An instrument with name '{entry['name']}' in language '{entry['language']}' already exists",
                        details={"name": entry["name"], "language": entry["language"]},
                    )

            # Generate UMIL ID
            umil_id = Instrument.generate_umil_id()

            # Create instrument (wikidata_id is None for user-created instruments)
            instrument = Instrument.objects.create(
                umil_id=umil_id,
                wikidata_id=None,
                hornbostel_sachs_class=hbs_class,
                source=instrument_source,
                created_by=request.user,
                verification_status="unverified",
            )

            # Track which languages have had a label assigned
            label_assigned = set()

            instrument_names_to_create = []

            for entry in entries:
                lang_code = entry["language"]
                name = entry["name"]
                source = entry["source"]

                # First name per language gets umil_label=True
                umil_label = lang_code not in label_assigned
                if umil_label:
                    label_assigned.add(lang_code)

                instrument_names_to_create.append(
                    InstrumentName(
                        instrument=instrument,
                        language=language_codes[lang_code],
                        name=name,
                        source_name=source,
                        umil_label=umil_label,
                        contributor=request.user,
                        verification_status="unverified",
                    )
                )

            # IMPORTANT: We use bulk_create() for performance (1 DB query vs N queries).
            # This is critical when users submit 10+ names per instrument.
            # HOWEVER: bulk_create() bypasses Django's validation system (full_clean(), signals).
            # Therefore, we MUST validate explicitly before bulk_create.
            # See validators.py for detailed explanation and future-proofing notes.
            try:
                validate_instrument_names(instrument_names_to_create)
                validate_umil_label_constraint(instrument_names_to_create)
            except ValidationError as ve:
                raise ValidationException(
                    ErrorCode.VALIDATION_ERROR,
                    get_error_message(ErrorCode.VALIDATION_ERROR),
                    details={"validation_errors": str(ve)},
                )

            # Create AVResource records if an image was provided.
            # File I/O is deferred to transaction.on_commit() below so that a
            # rollback (e.g. bulk_create failure) cannot leave orphaned files on disk.
            if image_file:
                # Process image to get ContentFile objects
                (
                    original_content,
                    thumbnail_content,
                    img_format,
                ) = process_uploaded_image(image_file, umil_id)

                # Create AVResource for original image (file saved in on_commit)
                av_resource = AVResource(
                    instrument=instrument,
                    type="image",
                    format=img_format,
                    source_name=image_source,
                    created_by=request.user,
                    is_thumbnail=False,
                )
                av_resource.save()
                instrument.default_image = av_resource

                # Create AVResource for thumbnail (file saved in on_commit)
                thumbnail_av = AVResource(
                    instrument=instrument,
                    type="image",
                    format=img_format,
                    source_name=image_source,
                    created_by=request.user,
                    is_thumbnail=True,
                )
                thumbnail_av.save()
                instrument.thumbnail = thumbnail_av
                instrument.save()

                # Defer file writes to after commit — prevents orphaned files on
                # rollback.  Trade-off: if the file save itself fails post-commit,
                # the AVResource rows exist but point to missing files.  That state
                # is detectable and recoverable; it is strictly better than silent
                # orphans with no DB record.
                def save_image_files():
                    av_resource.file.save(
                        f"{umil_id}.{img_format}", original_content, save=True
                    )
                    thumbnail_av.file.save(
                        f"{umil_id}.{img_format}", thumbnail_content, save=True
                    )

                transaction.on_commit(save_image_files)

            # Now safe to bulk create - validation passed
            InstrumentName.objects.bulk_create(instrument_names_to_create)

            # Schedule Solr indexing to run after transaction commits successfully.
            # Registered inside atomic() so that the closure over `instrument` and
            # the on_commit hook live in the same scope as the variable assignment.
            def schedule_indexing():
                try:
                    index_success = index_single_instrument(instrument.pk)
                    if not index_success:
                        # Mark for reindexing
                        instrument.needs_reindexing = True
                        instrument.save(update_fields=["needs_reindexing"])
                        logger.warning(
                            f"Instrument {instrument.pk} (UMIL ID: {instrument.umil_id}) was created but failed to index in Solr. "
                            f"Marked for reindexing. Run 'python manage.py reindex_failed' to retry."
                        )
                except Exception as e:
                    # Mark for reindexing on exception
                    instrument.needs_reindexing = True
                    instrument.save(update_fields=["needs_reindexing"])
                    logger.error(
                        f"Error indexing instrument {instrument.pk} (UMIL ID: {instrument.umil_id}) in Solr: {e}. "
                        f"Marked for reindexing.",
                        exc_info=True,
                    )

            transaction.on_commit(schedule_indexing)

        return success_response(
            "Instrument created successfully",
            status=201,
            instrument_id=instrument.pk,
            umil_id=umil_id,
        )

    except Exception as e:
        # Handle all exceptions and convert to safe responses
        # File writes are deferred to on_commit, so transaction rollbacks cannot
        # leave orphaned files.  Cleanup of deleted model instances is handled by
        # django_cleanup.
        return handle_exception(
            e,
            context="create_instrument",
            request_user=(
                request.user.username if request.user.is_authenticated else None
            ),
        )


@login_required
@require_http_methods(["POST"])
def check_duplicate_names(request: HttpRequest) -> JsonResponse:
    """
    Check if multiple instrument names already exist in database.
    Used by frontend validation to show inline errors before form submission.

    Expects JSON array: [{"language": "en", "name": "Flute"}, ...]
    Returns: {"duplicates": [{"language": "en", "name": "Flute", "exists": true}, ...]}
    """
    try:
        try:
            entries = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(
                ErrorCode.INVALID_JSON_FORMAT, "Invalid JSON format", status=400
            )

        if not isinstance(entries, list):
            return error_response(
                ErrorCode.VALIDATION_ERROR, "Expected array of entries", status=400
            )

        duplicates = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue

            language_code = entry.get("language")
            name = entry.get("name")

            if not language_code or not name:
                continue

            # Check if this name already exists in the database (case-insensitive)
            exists = InstrumentName.objects.filter(
                language__wikidata_code=language_code,
                name__iexact=name,
            ).exists()

            duplicates.append(
                {"language": language_code, "name": name, "exists": exists}
            )

        return JsonResponse({"duplicates": duplicates})

    except Exception as e:
        return handle_exception(
            e,
            context="check_duplicate_names",
            request_user=(
                request.user.username if request.user.is_authenticated else None
            ),
        )
