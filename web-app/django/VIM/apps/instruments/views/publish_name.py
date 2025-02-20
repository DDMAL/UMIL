""" Django view to handle publishing to Wikidata using OAuth. """

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from VIM.apps.instruments.models import Instrument, Language, InstrumentName
from VIM.apps.instruments.views.wiki_apis import add_info_to_wikidata_entity


@login_required
def publish_name(request):
    """
    View to publish new instrument names to Wikidata using OAuth.

    This view expects a POST request with the JSON body:
    {
        "wikidata_id": "Q12345",
        "entries": [
            {
                "language": "en",
                "name": "English label",
                "source": "Source name",
                "description": "Description",
                "alias": "Alias"
            },
            {
                "language": "fr",
                "name": "French label",
                ...
            }
        ],
        "publish_to_wikidata": true,
    }

    Returns:
        JsonResponse: JSON response with status and message
    """
    if request.method == "POST":
        # Parse the JSON request body
        data = json.loads(request.body)
        wikidata_id = data.get("wikidata_id")
        entries = data.get("entries", [])
        publish_to_wikidata = data.get("publish_to_wikidata", False)
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

            # If publishing to Wikidata is requested, handle OAuth authorization
            access_token = None
            if publish_to_wikidata:
                # Extract the access_token from the cookie
                access_token = request.COOKIES.get("wikidata_access_token")
                if not access_token:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": "Failed to retrieve access token",
                        }
                    )

            # Process each entry: save locally, and conditionally publish to Wikidata
            for entry in entries:
                language_code = entry["language"]
                name = entry["name"]
                source = entry["source"]
                description = entry.get("description", "")
                alias = entry.get("alias", "")

                # Publish each entry to Wikidata if requested
                if publish_to_wikidata:
                    # Add the label
                    response_label = add_info_to_wikidata_entity(
                        "add_label", access_token, wikidata_id, name, language_code
                    )
                    if "errors" in response_label:
                        return JsonResponse(
                            {
                                "status": "error",
                                "message": f"Failed to publish label: {response_label}",
                            }
                        )

                    # Add the description if provided
                    if description:
                        response_desc = add_info_to_wikidata_entity(
                            "add_description",
                            access_token,
                            wikidata_id,
                            description,
                            language_code,
                        )
                        if "errors" in response_desc:
                            return JsonResponse(
                                {
                                    "status": "error",
                                    "message": f"Failed to publish description: {response_desc}",
                                }
                            )

                    # Add the alias if provided
                    if alias:
                        response_alias = add_info_to_wikidata_entity(
                            "add_aliases",
                            access_token,
                            wikidata_id,
                            alias,
                            language_code,
                        )
                        if "errors" in response_alias:
                            return JsonResponse(
                                {
                                    "status": "error",
                                    "message": f"Failed to publish alias: {response_alias}",
                                }
                            )

                # Save entries to the local database
                language = Language.objects.get(wikidata_code=language_code)
                InstrumentName.objects.create(
                    instrument=instrument,
                    language=language,
                    name=name,
                    source_name=source,
                    description=description,
                )
                if alias:
                    InstrumentName.objects.create(
                        instrument=instrument,
                        language=language,
                        name=alias,
                        source_name=source,
                    )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Data saved and published successfully!",
                }
            )

        except Instrument.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Instrument not found"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": "" + str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method"})
