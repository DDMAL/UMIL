"""This module imports possible languages for instrument names from Wikidata."""

import requests
from django.core.management.base import BaseCommand
from VIM.apps.instruments.models import Language

WIKIDATA_URL = "https://www.wikidata.org/w/api.php"

HEADERS = {
    "User-Agent": "UMIL/0.1.0 (https://vim.simssa.ca/; https://ddmal.music.mcgill.ca/)"
}


def get_languages_from_wikidata():
    """
    Fetches the list of languages from Wikidata using the Wikidata API.

    The API endpoint used is the `siteinfo` module with the `languages` parameter.
    For more information, see:
        https://www.wikidata.org/wiki/Special:ApiHelp/query%2Bsiteinfo

    Example API request in the API sandbox:
        https://www.wikidata.org/wiki/Special:ApiSandbox#action=query&format=json&prop=&list=&meta=siteinfo&formatversion=2&siprop=languages

    Returns:
        list: A list of dictionaries containing language information.

        For example:
        [
            {
                "code": "aa",
                "bcp47": "aa",
                "name": "Qafár af"
            },
            {
                "code": "aae",
                "bcp47": "aae",
                "name": "Arbërisht"
            },
            ...
        ]
    """

    # Define the API endpoint and parameters to get the list of languages
    params = {
        "action": "query",
        "format": "json",
        "prop": "",
        "list": "",
        "meta": "siteinfo",
        "formatversion": "2",
        "siprop": "languages",
    }

    # Make the request to the Wikidata API
    response = requests.get(WIKIDATA_URL, params=params, headers=HEADERS, timeout=50)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the language list from the response
        languages = data.get("query", {}).get("languages", [])
        return languages
    else:
        print(f"Error: Failed to fetch data. Status code {response.status_code}")
        return []


def get_language_details(language_codes):
    """
    Fetches the details of the specified languages from Wikidata using the Wikidata API.

    The API endpoint used is the `languageinfo` module with the `liprop` parameter.
    For more information, see:
        https://www.wikidata.org/w/api.php?action=help&modules=query%2Blanguageinfo

    Example API request in the API sandbox:
        https://www.wikidata.org/wiki/Special:ApiSandbox#action=query&format=json&prop=&list=&meta=languageinfo&formatversion=2&liprop=autonym%7Ccode%7Cname&licode=aa%7Caae

    Args:
        language_codes (list): A list of language codes for which details are to be fetched.

    Returns:
        dict: A dictionary containing language details with the language code as the key.

        For example:
        {
            "aa": {
                "code": "aa",
                "autonym": "Qafár af",
                "name": "Afar"
            },
            "aae": {
                "code": "aae",
                "autonym": "Arbërisht",
                "name": "Arbëresh"
            }
            ...
        }
    """

    # Define the API endpoint and parameters to get the language details
    params = {
        "action": "query",
        "format": "json",
        "prop": "",
        "meta": "languageinfo",
        "formatversion": "2",
        "liprop": "code|autonym|name",
        "licode": "|".join(language_codes),
    }

    # Make the request to the Wikidata API
    response = requests.get(WIKIDATA_URL, params=params, headers=HEADERS, timeout=50)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the language details from the response
        language_details = data.get("query", {}).get("languageinfo", {})
        return language_details
    else:
        print(f"Error: Failed to fetch data. Status code {response.status_code}")
        return None


def get_language_directions_from_sparql(url: str):
    """
    Fetches the text direction for all languages available in Wikidata using SPARQL.
    Returns a dictionary mapping each language code to its text direction.
    """
    query = """
    SELECT ?code (MIN(?directionLabel) AS ?direction) WHERE { # some languages have two directions: MIN fetches it to ltr
        ?lang wdt:P305 ?code .        # IETF language tag
        ?lang wdt:P282 ?script .      # writing system
        ?script wdt:P1406 ?directionItem .   # script direction
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en" .
            ?directionItem rdfs:label ?directionLabel .
        }
        } GROUP BY ?code
    """

    response = requests.get(
        url, params={"query": query, "format": "json"}, headers=HEADERS, timeout=200
    )
    data = response.json()

    directions = {}
    for item in data.get("results", {}).get("bindings", []):
        code = item["code"]["value"].lower()
        direction_label = item["direction"]["value"]
        if "right-to-left" in direction_label:
            directions[code] = "rtl"
        else:
            directions[code] = "ltr"
    return directions


class Command(BaseCommand):
    """
    The import_languages command populates the database with languages in which instrument
    names can be provided in UMIL. It fetches the language list from Wikidata, retrieves the
    'wikidata_code', 'autonym', 'en_label', and 'direction', and stores them in the database.
    """

    help = "Imports possible languages for instrument names from Wikidata."

    WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

    def handle(self, *args, **options):
        # Fetch the list of languages
        fetched_dir = 0
        languages = get_languages_from_wikidata()
        language_codes = [lang.get("code") for lang in languages]

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully fetched {len(language_codes)} language codes."
            )
        )

        # Fetch text directions for all language codes (can be batched if needed)
        directions = get_language_directions_from_sparql(self.WIKIDATA_SPARQL_URL)

        # Fetch details for specific language codes, 50 at a time
        for i in range(0, len(language_codes), 50):
            language_batch = language_codes[i : i + 50]
            language_details = get_language_details(language_batch)
            if language_details:
                for lang in language_details:
                    wikidata_code = language_details[lang]["code"]
                    en_label = language_details[lang]["name"]
                    autonym = language_details[lang]["autonym"]
                    if wikidata_code in directions:
                        direction = directions[wikidata_code]
                        fetched_dir += 1
                    else:
                        direction = "ltr"

                    Language.objects.update_or_create(
                        wikidata_code=wikidata_code,
                        defaults={
                            "en_label": en_label,
                            "autonym": autonym,
                            "html_direction": direction,
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {Language.objects.count()} languages."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully fetched {Language.objects.filter(wikidata_code__in=directions.keys()).count()} directions."
            )
        )
