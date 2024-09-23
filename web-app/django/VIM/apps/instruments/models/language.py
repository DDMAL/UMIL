from django.db import models


class Language(models.Model):
    wikidata_code = models.CharField(
        unique=True, blank=False, help_text="Language code in Wikidata"
    )
    en_label = models.CharField(blank=False, help_text="Language label in English")
    autonym = models.CharField(
        blank=False, help_text="Language label in the language itself"
    )
