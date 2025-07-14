"""Django view to handle user input to UMIl database"""

import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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
            language = Language.objects.get(wikidata_code=language_code)

            name = entry["name"]
            source = entry["source"]

            # If the instrument already has a name in specified language, save as alias
            if instrument.instrumentname_set.filter(language=language).exists():
                InstrumentName.objects.create(
                    instrument=instrument,
                    language=language,
                    name=name,
                    source_name=source,
                    is_alias=True,
                    contributor=request.user,
                )
            # If the instrument does not have a name in specified language, save as primary name
            else:
                InstrumentName.objects.create(
                    instrument=instrument,
                    language=language,
                    name=name,
                    source_name=source,
                    is_alias=False,
                    contributor=request.user,
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
@require_POST
def delete_name(request):
    """View to delete an instrument name from UMIL database."""

    if request.method == "DELETE":
        data = json.loads(request.body)
        name_id = data.get("instrument_name_id")
    try:
        instrument_name = InstrumentName.objects.get(
            id=name_id, contributor=request.user
        )
        instrument_name.delete()
        return JsonResponse({"status": "success"})
    except InstrumentName.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Not found or not allowed"}, status=403
        )
