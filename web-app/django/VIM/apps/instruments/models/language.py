from django.db import models


class Language(models.Model):
    wikidata_code = models.CharField(
        unique=True, blank=False, help_text="Language code in Wikidata"
    )
    en_label = models.CharField(blank=False, help_text="Language label in English")
    autonym = models.CharField(
        blank=False, help_text="Language label in the language itself"
    )
    direction = models.CharField(
        max_length=3,
        choices=[
            ("ltr", "Left-to-Right"),
            ("rtl", "Right-to-Left"),
        ],
        default="ltr",
        help_text="Text direction",
    )

    def __str__(self):
        return f"{self.en_label}"
