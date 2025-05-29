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
        language_code = data.get("language")
        entry = data.get("entry")
        if not wikidata_id or not language_code or not entry:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing required data",
                }
            )     
    try:
        # Fetch the instrument from the database
        instrument = Instrument.objects.get(wikidata_id=wikidata_id)
        # Fetch the language from the database
        language = Language.objects.get(wikidata_code=language_code)

        # Extract data from the entry
        name = entry["name"]
        source = entry["source"]
        alias = entry["alias"]

        # Save entries to the local database
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
        language_code = data.get("language")
        entries = data.get("entries", [])
        if not wikidata_id or not language_code or not entries:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing required data",
                }
            )     
    try:
        # Fetch the instrument from the database
        instrument = Instrument.objects.get(wikidata_id=wikidata_id)
        # Fetch the language from the database
        language = Language.objects.get(wikidata_code=language_code)
        
        # Process each entry: save to UMIL database
        for entry in entries:
            
            source = entry["source"]
            alias = entry["alias"]

            # Save entries to the local database
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
    