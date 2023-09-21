from django.db import models


class Language(models.Model):
    wikidata_code = models.CharField(max_length=10, unique=True, blank=False)
    wikidata_id = models.CharField(max_length=20,unique=True)
    en_label = models.CharField(
        max_length=50, blank=False, help_text="Language label in English"
    )
    autonym = models.CharField(
        max_length=50, blank=False, help_text="Language label in the language itself"
    )
