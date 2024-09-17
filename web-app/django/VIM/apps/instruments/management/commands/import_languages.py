"""This module imports possible languages for instrument names from Wikidata."""

import requests
from django.core.management.base import BaseCommand
from VIM.apps.instruments.models import Language


class Command(BaseCommand):
    """
    The import_languages command populates the database with languages in which instrument
    names can be provided in VIM. It fetches the language list from Wikidata, retrieves the
    'wikidata_code', 'wikidata_id', 'autonym', and 'en_label', and stores them in the database.
    """

    help = "Imports possible languages for instrument names from Wikidata."

    WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

    def handle(self, *args, **options):
        query = """
        SELECT ?language ?languageLabel ?ISO639code ?autonym WHERE {
          ?language wdt:P31 wd:Q34770;   # Instance of a natural language
                   wdt:P424 ?ISO639code; # ISO 639 code
                   rdfs:label ?autonym filter (lang(?autonym) = ?ISO639code).
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        """

        headers = {"Accept": "application/sparql-results+json"}
        response = requests.get(
            self.WIKIDATA_SPARQL_URL,
            params={"query": query},
            headers=headers,
            timeout=50,
        )
        data = response.json()

        for item in data["results"]["bindings"]:
            wikidata_code = item["ISO639code"]["value"]
            wikidata_id = item["language"]["value"].split("/")[-1]
            en_label = item["languageLabel"]["value"]
            autonym = item["autonym"]["value"]

            self.stdout.write(
                wikidata_code, "-", wikidata_id, "-", en_label, "-", autonym
            )

            Language.objects.update_or_create(
                wikidata_code=wikidata_code,
                defaults={
                    "wikidata_id": wikidata_id,
                    "en_label": en_label,
                    "autonym": autonym,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {len(data['results']['bindings'])} languages."
            )
        )
