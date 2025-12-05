from django.contrib import admin
from VIM.apps.instruments.models import (
    Instrument,
    InstrumentName,
    InstrumentNameSource,
    Source,
    Language,
    AVResource,
)

admin.site.register(Instrument)
admin.site.register(InstrumentNameSource)
admin.site.register(Language)
admin.site.register(AVResource)


class InstrumentNameSourceInline(admin.TabularInline):
    model = InstrumentNameSource
    extra = 1
    fields = (
        "source",
        "contributor",
    )
    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        """
        Make fields read-only for users in the 'reviewer' group.
        """
        if request.user.groups.filter(name="reviewer").exists():
            return ("source", "contributor")
        return super().get_readonly_fields(request, obj)


@admin.register(InstrumentName)
class InstrumentNameAdmin(admin.ModelAdmin):
    list_filter = ("verification_status", "on_wikidata")
    search_fields = (
        "name",
        "sources__name",
        "instrument__wikidata_id",
    )
    inlines = [InstrumentNameSourceInline]
    list_editable = ("verification_status",)  # Allow editing of verification_status
    list_display = (
        "name",
        "instrument",
        "language",
        "umil_label",
        "on_wikidata",
        "verification_status",
        "all_sources",
    )  # Show all sources in list view

    def get_readonly_fields(self, request, obj=None):
        """
        Make fields read-only for users in the 'reviewer' group.
        """
        if request.user.groups.filter(name="reviewer").exists():
            return (
                "instrument",
                "language",
                "name",
                "umil_label",
                "on_wikidata",
            )
        return super().get_readonly_fields(request, obj)

    def all_sources(self, obj):
        """
        Display all associated source names for this instrument name
        """
        return ", ".join(source.name for source in obj.sources.all())

    all_sources.short_description = "Sources"


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_visible")
    list_filter = ("is_visible",)
    search_fields = ("name",)
    list_editable = ("is_visible",)  # Allow editing of is_visible
