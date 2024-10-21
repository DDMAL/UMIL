""" Django view to handle publishing to Wikidata. """

import json
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from VIM.apps.instruments.models import Instrument, Language, InstrumentName
from VIM.apps.instruments.views.wiki_apis import (
    get_csrf_token,
    add_info_to_wikidata_entity,
)


@csrf_protect
def publish_name(request):
    """
    View to publish new instrument names to Wikidata.

    This view expects a POST request with the following JSON body like this:
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
        "publish_to_wikidata": true
    }

    The view will publish the provided entries to the Wikidata entity with the given ID.

    Returns:
        JsonResponse: JSON response with status and message
    """

    if request.method == "POST":
        # Parse the JSON request body
        data = json.loads(request.body)
        username = "YOUR_USERNAME"  # Replace with actual username
        password = "YOUR_PASSWORD"  # Replace with actual credentials
        wikidata_id = data.get("wikidata_id")
        entries = data.get("entries")
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

            # Process each entry: save locally, and conditionally publish to Wikidata
            if publish_to_wikidata:
                csrf_token, lgusername, error_message = get_csrf_token(
                    username, password
                )

                # Check if there was an error
                if error_message:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": f"Failed to get CSRF token: {error_message}",
                        }
                    )
            for entry in entries:
                language_code = entry["language"]
                name = entry["name"]
                source = entry["source"]
                description = entry["description"]
                alias = entry["alias"]

                # Get the language object
                language = Language.objects.get(wikidata_code=language_code)

                # Optionally publish to Wikidata
                if publish_to_wikidata:
                    # Publish the new label to Wikidata
                    response_label = add_info_to_wikidata_entity(
                        "wbsetlabel",
                        csrf_token,
                        wikidata_id,
                        name,
                        language_code,
                        lgusername,
                    )
                    if "error" in response_label:
                        return JsonResponse(
                            {
                                "status": "error",
                                "message": f"Failed to publish label: {response_label}",
                            }
                        )

                    # Publish the new description to Wikidata
                    response_desc = add_info_to_wikidata_entity(
                        "wbsetdescription",
                        csrf_token,
                        wikidata_id,
                        description,
                        language_code,
                        lgusername,
                    )
                    if "error" in response_desc:
                        return JsonResponse(
                            {
                                "status": "error",
                                "message": f"Failed to publish description: {response_desc}",
                            }
                        )

                    # Publish the new alias to Wikidata
                    response_alias = add_info_to_wikidata_entity(
                        "wbsetaliases",
                        csrf_token,
                        wikidata_id,
                        alias,
                        language_code,
                        lgusername,
                    )
                    if "error" in response_alias:
                        return JsonResponse(
                            {
                                "status": "error",
                                "message": f"Failed to publish alias: {response_alias}",
                            }
                        )

                # Save to the local database
                # for "name" in "lang" with "description"
                InstrumentName.objects.create(
                    instrument=instrument,
                    language=language,
                    name=name,
                    source_name=source,
                    description=description,
                )
                # if alias is provided, save to the local database
                if alias:
                    # for "alias" in language "lang"
                    InstrumentName.objects.create(
                        instrument=instrument,
                        language=language,
                        name=alias,
                        source_name=source,
                    )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Data saved successfully!",
                }
            )
        except Instrument.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Instrument not found"})
    return JsonResponse({"status": "error", "message": "Invalid request method"})
