from django.contrib import admin
from VIM.apps.instruments.models import Instrument, InstrumentName, Language, AVResource

admin.site.register(Instrument)
# admin.site.register(InstrumentName)
admin.site.register(Language)
admin.site.register(AVResource)


@admin.register(InstrumentName)
class InstrumentNameAdmin(admin.ModelAdmin):
    list_filter = ("status", "is_approved", "on_wikidata")  # Filter by status
    search_fields = (
        "name",
        "source_name",
        "instrument__wikidata_id",
    )  # Search by name, source name, and instrument wikidata ID

    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields except 'status' read-only for users in the 'reviewer' group.
        """
        if request.user.groups.filter(name="reviewer").exists():
            return (
                "instrument",
                "language",
                "name",
                "source_name",
                "is_alias",
                "contributor",
                "on_wikidata",
                "is_approved",
            )
        return super().get_readonly_fields(request, obj)
