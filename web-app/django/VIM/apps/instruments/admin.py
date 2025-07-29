from django.contrib import admin
from VIM.apps.instruments.models import Instrument, InstrumentName, Language, AVResource

admin.site.register(Instrument)
admin.site.register(Language)
admin.site.register(AVResource)


@admin.register(InstrumentName)
class InstrumentNameAdmin(admin.ModelAdmin):
    list_filter = ("verification_status", "on_wikidata")  # Filter by status
    search_fields = (
        "name",
        "source_name",
        "instrument__wikidata_id",
    )  # Search by name, source name, and instrument wikidata ID

    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields except 'verification_status' read-only for users in the 'reviewer' group.
        """
        if request.user.groups.filter(name="reviewer").exists():
            return (
                "instrument",
                "language",
                "name",
                "source_name",
                "umil_label",
                "contributor",
                "on_wikidata",
            )
        return super().get_readonly_fields(request, obj)
