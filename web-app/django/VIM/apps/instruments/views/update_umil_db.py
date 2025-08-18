"""Django view to handle user input to UMIl database"""

import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from VIM.apps.instruments.models import Instrument, Language, InstrumentName
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

    instrument_names_to_create = []

    for entry in entries:
        language_code: str = entry["language"]
        name: str = entry["name"]
        source: str = entry["source"]

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

        # Prepare the InstrumentName object
        instrument_names_to_create.append(
            InstrumentName(
                instrument=instrument,
                language=language_obj,
                name=name,
                source_name=source,
                contributor=request.user,
            )
        )

    # Bulk create all InstrumentName objects
    InstrumentName.objects.bulk_create(instrument_names_to_create)

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

    # If user is a superuser or created the name, allow deletion
    if request.user.is_superuser or instrument_name.contributor == request.user:
        instrument_name.deleted = True  # Soft delete the name
        instrument_name.save()  # Don't forget to save the changes

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
