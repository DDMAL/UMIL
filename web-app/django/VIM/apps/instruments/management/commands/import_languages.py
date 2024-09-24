"""This module imports possible languages for instrument names from Wikidata."""

import requests
from django.core.management.base import BaseCommand
from VIM.apps.instruments.models import Language

WIKIDATA_URL = "https://www.wikidata.org/w/api.php"


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
    response = requests.get(WIKIDATA_URL, params=params, timeout=50)

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
    response = requests.get(WIKIDATA_URL, params=params, timeout=50)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the language details from the response
        language_details = data.get("query", {}).get("languageinfo", {})
        return language_details
    else:
        print(f"Error: Failed to fetch data. Status code {response.status_code}")
        return None


class Command(BaseCommand):
    """
    The import_languages command populates the database with languages in which instrument
    names can be provided in UMIL. It fetches the language list from Wikidata, retrieves the
    'wikidata_code', 'autonym', and 'en_label', and stores them in the database.
    """

    help = "Imports possible languages for instrument names from Wikidata."

    WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

    def handle(self, *args, **options):
        # Fetch the list of languages
        languages = get_languages_from_wikidata()
        language_codes = [lang.get("code") for lang in languages]

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully fetched {len(language_codes)} language codes."
            )
        )

        # Fetch details for specific language codes, 50 at a time
        for i in range(0, len(language_codes), 50):
            language_batch = language_codes[i : i + 50]
            language_details = get_language_details(language_batch)
            if language_details:
                for lang in language_details:
                    wikidata_code = language_details[lang]["code"]
                    en_label = language_details[lang]["name"]
                    autonym = language_details[lang]["autonym"]

                    Language.objects.update_or_create(
                        wikidata_code=wikidata_code,
                        defaults={"en_label": en_label, "autonym": autonym},
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {Language.objects.count()} languages."
            )
        )
