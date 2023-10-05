from django.core.management.base import BaseCommand
from VIM.apps.instruments.models import Language


class Command(BaseCommand):
    """
    The import_languages command populates the database with languages in which instrument
    names can be provided in VIM.

    NOTE: For now, this script only imports English and French.
    """

    help = "Imports possible languages for instrument names from Wikidata."

    def handle(self, *args, **options):
        Language.objects.create(
            wikidata_code="fr",
            wikidata_id="Q150",
            en_label="french",
            autonym="français",
        )
        Language.objects.create(
            wikidata_code="en",
            wikidata_id="Q1860",
            en_label="english",
            autonym="english",
        )
