"""Django view to handle user input to UMIl database"""

import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from VIM.apps.instruments.models import Instrument, Language, InstrumentName


@login_required
@require_POST
def add_name(request):
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
    data = json.loads(request.body)
    wikidata_id = data.get("wikidata_id")
    entries = data.get("entries", [])
    if not wikidata_id or not entries:
        return JsonResponse(
            {
                "status": "error",
                "message": "Missing required data",
            },
            status=400,
        )
    # Fetch the instrument from the database, if it does not exist return does not exist error
    try:   
        instrument = Instrument.objects.get(wikidata_id=wikidata_id)
    except Instrument.DoesNotExist:
        return JsonResponse(
            {
                "status": "error", 
                "message": "Instrument not found"
            },
            status=404,    
        )
    
    # create dictionary to map language codes to Language objects
    language = {lang.wikidata_code: lang for lang in Language.objects.all()}

    instrument_names_to_create = []

    for entry in entries:
        language_code = entry["language"]
        name = entry["name"]
        source = entry["source"]
        
        # Validate that entry info is provided
        if not name or not source or not language_code:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing entry information",
                },
                status=400,
            )
        
        # Find language object from language code
        if language.get(language_code) is None:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Language '{language_code}' not found",
                },
                status=400,
            )


        # Check if the instrument already has a name in the specified language
        is_alias = instrument.instrumentname_set.filter(language__wikidata_code=language_code).exists()

        # Prepare the InstrumentName object
        instrument_names_to_create.append(
            InstrumentName(
                instrument=instrument,
                language=language.get(language_code),
                name=name,
                source_name=source,
                is_alias=is_alias,
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

@login_required
@require_http_methods(["DELETE"])
def delete_name(request):
    """View to delete an instrument name from UMIL database."""

    # Parse the JSON request body
    data = json.loads(request.body)
    name_id = data.get("instrument_name_id")
    print(name_id, flush=True)
    
    # Check if name_id is provided, if not return 400 error
    if not name_id:
        return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing required data",
                },
                status = 400,
            )
    try:
        instrument_name = InstrumentName.objects.get(id=name_id)

        # If user is a superuser or created the name, allow deletion
        if request.user.is_superuser or instrument_name.contributor == request.user:
            instrument_name.delete()
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Instrument name deleted successfully",
                },
                status = 200,
            )
        elif instrument_name.contributor is None:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "This name was not created by any user, it cannot be deleted",
                },
                status = 403,
            )
        else: 
            return JsonResponse(
                {
                    "status": "error",
                    "message": "You are not allowed to delete this name",
                },
                status = 403,
            )
        
    except InstrumentName.DoesNotExist:
        return JsonResponse(
            {
                "status": "error", 
                "message": "Instrument name not found",
            },
            status = 404,
        )
