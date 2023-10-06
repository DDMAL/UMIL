from django.core.management.base import BaseCommand
from VIM.apps.instruments.models import Language

class Command(BaseCommand):
    help = "Imports language objects"

    def handle(self, *args, **options):
        Language.objects.create(wikidata_code="fr", wikidata_id= "Q150", en_label="french", autonym="français")
        Language.objects.create(wikidata_code="en", wikidata_id= "Q1860", en_label="english", autonym="english")
