""" Django view to handle user input to UMIl database """

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from VIM.apps.instruments.models import Instrument, Language, InstrumentName

@login_required
def add_name(request):
    """
    View to add new instrument names to UMIL database.

    This view expects a POST request with the JSON body:
    {
        "wikidata_id": "Q12345",
        "language": "en",
        "entry":
            {
                "name": "English label",
                "source": "Source name",
                "description": "Description",
                "alias": "Alias"
            },
    }

    Returns:
        JsonResponse: JSON response with status and message
    """
    if request.method == "POST":
        # Parse the JSON request body
        data = json.loads(request.body)
        wikidata_id = data.get("wikidata_id")
        entry = data.get("entry")
        if not wikidata_id or not entry:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing required data",
                }
            )     
    try:
        # Fetch the instrument from the database
        instrument = Instrument.objects.get(wikidata_id=wikidata_id)

        # Extract data from the entry
        language_code = entry["language"]
        name = entry["name"]
        source = entry["source"]
        alias = entry.get("alias", "")

        # Save entries to the local database
        language = Language.objects.get(wikidata_code=language_code)
        InstrumentName.objects.create(
            instrument=instrument,
            language=language,
            name=name,
            source_name=source,
            is_verified=False,
            is_alias=False
        )
        # Save to the InstrumentAlias table if alias is provided 
        if alias:
            InstrumentName.objects.create(
                instrument_name=instrument,
                alias=alias,
                source_name=source,
                is_verified=False,
                is_alias=True
            )
            
        return JsonResponse(
                {
                    "status": "success",
                    "message": "Data saved successfully!",
                }
            )

    except Instrument.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Instrument not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": "" + str(e)})
    
@login_required
def add_alias(request):
    """
    View to add new instrument alias to UMIL database.

    This view expects a POST request with the JSON body:
    {
        "wikidata_id": "Q12345",
        "language": "en",
        "entries": [
            {
                "alias": "Alias"
                "source": "Source name",
                
            },
            {
                "alias": "Alias"
                "source": "Source name",
            },
            ...
        ],
    }

    Returns:
        JsonResponse: JSON response with status and message
    """
    if request.method == "POST":
        # Parse the JSON request body
        data = json.loads(request.body)
        wikidata_id = data.get("wikidata_id")
        entries = data.get("entries", [])
        if not wikidata_id or not entries:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing required data",
                }
            )     
    try:
        # Fetch the instrument from the database
        instrument = Instrument.objects.get(wikidata_id=wikidata_id)

        # Process each entry: save to UMIL database
        for entry in entries:

            # Extract data from the entry
            language_code = entry["language"]
            source = entry["source"]
            alias = entry.get("alias", "")

            # Save entries to the local database
            language = Language.objects.get(wikidata_code=language_code)
            InstrumentName.objects.create(
                instrument=instrument,
                language=language,
                name=alias,
                source_name=source,
                is_verified=False,
                is_alias=True
            )
            
        return JsonResponse(
                {
                    "status": "success",
                    "message": "Data saved successfully!",
                }
            )

    except Instrument.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Instrument not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": "" + str(e)})
    