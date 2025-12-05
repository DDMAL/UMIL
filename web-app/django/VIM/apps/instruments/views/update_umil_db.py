"""Django view to handle user input to UMIl database"""

import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from VIM.apps.instruments.models import (
    Instrument,
    InstrumentName,
    InstrumentNameSource,
    Source,
    Language,
)
from typing import Any, Dict, List


def add_name(request: HttpRequest) -> JsonResponse:
    """
    View to add new instrument names to UMIL database.

    This view expects a POST request with the JSON body:
    {
        "wikidata_id": "Q12345",
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
    # Parse the JSON request body, if it fails return missing data error
    data: Dict[str, Any] = json.loads(request.body)
    wikidata_id: str = data.get("wikidata_id")
    entries: List[Dict[str, str]] = data.get("entries", [])
    if not wikidata_id or not entries:
        return JsonResponse(
            {
                "status": "error",
                "message": "Missing required data",
            },
            status=400,
        )
    # Fetch the instrument from the database, if it does not exist return does not exist error
    instrument = get_object_or_404(Instrument, wikidata_id=wikidata_id)

    # create dictionary to map language codes to Language objects
    language = {lang.wikidata_code: lang for lang in Language.objects.all()}

    # considering entries with multiple of the same language, create a dictionary to track if a label has
    # been assigned to a previous entry
    entry_labels = {entry["language"]: False for entry in entries}

    # Deduplicate the entries with respect to language, name, and source: A user cannot suggest the same source for a label multiple times
    unique_entries = {
        (e["language"], e["name"].strip(), e["source"].strip()) for e in entries
    }

    # Find which sources already exist in the database
    all_source_names = {source for (_, _, source) in unique_entries}
    existing_sources_qs = Source.objects.filter(name__in=all_source_names)
    existing_sources = {s.name: s for s in existing_sources_qs}

    # Bulk create missing sources
    missing_source_names = all_source_names - set(existing_sources.keys())
    sources_to_create = [
        Source(name=src, is_visible=True) for src in missing_source_names
    ]
    if sources_to_create:
        Source.objects.bulk_create(sources_to_create)

    instrument_name_sources_to_create = []

    for language_code, name, source in unique_entries:
        # Validate that entry info is provided
        if not name or not source or not language_code:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing entry information",
                },
                status=400,
            )

        # Find language object from language code dictionary
        language_obj: Language = language.get(language_code)

        # Check if the name exists in UMIL_db
        existing_name = InstrumentName.objects.filter(
            instrument=instrument,
            language__wikidata_code=language_code,
            name__iexact=name,
        ).first()
        source_obj, _ = Source.objects.get_or_create(name=source)

        if existing_name:
            # Check if the InstrumentNameSource exists with this contributor
            insource_exists = InstrumentNameSource.objects.filter(
                instrument_name=existing_name,
                source=source_obj,
                contributor=request.user,
            ).exists()
            if not insource_exists:
                instrument_name_sources_to_create.append(
                    InstrumentNameSource(
                        instrument_name=existing_name,
                        source=source_obj,
                        contributor=request.user,
                    )
                )
            # Skip further creation if InstrumentName already exists
            continue

        # If name does not exist, create it, track umil_label
        if entry_labels[language_code]:
            umil_label = False
        else:
            umil_label: bool = not (
                instrument.instrumentname_set.filter(
                    language__wikidata_code=language_code
                ).exists()
            )
            entry_labels[language_code] = True  # Mark that this language now has a name

        instrument_name_obj = InstrumentName.objects.create(
            instrument=instrument,
            language=language_obj,
            name=name,
            umil_label=umil_label,
            on_wikidata=False,
            verification_status="unverified",
        )
        instrument_name_sources_to_create.append(
            InstrumentNameSource(
                instrument_name=instrument_name_obj,
                source=source_obj,
                contributor=request.user,
            )
        )

    # Bulk create all InstrumentNameSource objects
    InstrumentNameSource.objects.bulk_create(instrument_name_sources_to_create)

    return JsonResponse(
        {
            "status": "success",
            "message": "All entries saved successfully",
        },
        status=200,
    )


def delete_name(request: HttpRequest) -> JsonResponse:
    """View to delete an instrument name from UMIL database."""

    # Parse the JSON request body
    data: Dict[str, Any] = json.loads(request.body)
    name_id: str = data.get("instrument_name_id")
    source_name: str = data.get("source_name")

    # Check if name_id is provided, if not return 400 error
    if not name_id:
        return JsonResponse(
            {
                "status": "error",
                "message": "Missing required data",
            },
            status=400,
        )

    instrument_name = get_object_or_404(InstrumentName, id=name_id)
    source_obj = get_object_or_404(Source, name=source_name)

    # Todo: add logic for superuser deletion

    # If user is a contributor to any linked InstrumentNameSource, allow link deletion
    if InstrumentNameSource.objects.filter(
        instrument_name=instrument_name, contributor=request.user, source=source_obj
    ).exists():
        InstrumentNameSource.objects.filter(
            instrument_name=instrument_name, contributor=request.user, source=source_obj
        ).delete()
        # If no sources are left, delete the instrument name
        if instrument_name.source_links.count() == 0:
            umil_status = instrument_name.umil_label
            instrument_name.delete()
            # If the name being deleted is the UMIL label,
            # restore UMIL label to another InstrumentName if one exists
            if umil_status:
                other_names = InstrumentName.objects.filter(
                    instrument=instrument_name.instrument,
                    language=instrument_name.language,
                )
                next_label = other_names.first()
                if next_label:
                    next_label.umil_label = True
                    next_label.save()
        return JsonResponse(
            {
                "status": "success",
                "message": "Instrument name deleted successfully",
            },
            status=200,
        )
    else:
        return JsonResponse(
            {
                "status": "error",
                "message": "You are not allowed to delete this name",
            },
            status=403,
        )


@login_required
@require_http_methods(["POST", "DELETE"])
def update_umil_db(request: HttpRequest, pk: int) -> JsonResponse:
    if request.method == "POST":
        return add_name(request)

    elif request.method == "DELETE":
        return delete_name(request)
