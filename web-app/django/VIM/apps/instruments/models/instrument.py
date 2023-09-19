from django.db import models


class Instrument(models.Model):
    wikidata_id = models.IntegerField(unique=True, primary_key=True)
    # default_image
    hornbostel_sachs_class = models.CharField(max_length=50, blank=True)
    mimo_class = models.CharField(max_length=50, blank=True)
