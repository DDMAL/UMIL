from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def migrate_strings_to_objects(apps, schema_editor):
    Instrument = apps.get_model("instruments", "Instrument")
    HornbostelSachs = apps.get_model("instruments", "HornbostelSachs")

    # We use a raw queryset or values to avoid potential model logic issues
    for inst in Instrument.objects.exclude(hornbostel_sachs_class__isnull=True):
        hbs_string = inst.hornbostel_sachs_class

        # Create the new object to link to
        hbs_obj = HornbostelSachs.objects.create(
            hbs_class=hbs_string,
            instrument=inst,
            is_main=True,
            review_status="unverified",
        )

        # Update the character column with the integer ID
        # PostgreSQL will allow this temporarily before the type change
        Instrument.objects.filter(pk=inst.pk).update(hornbostel_sachs_class=hbs_obj.id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("instruments", "0013_alter_avresource_format_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="HornbostelSachs",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "hbs_class",
                    models.CharField(
                        help_text="Hornbostel-Sachs classification",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "is_main",
                    models.BooleanField(
                        default=False,
                        help_text="Is this the main HBS classification for this instrument?",
                    ),
                ),
                (
                    "review_status",
                    models.CharField(
                        choices=[
                            ("verified", "Verified"),
                            ("unverified", "Unverified"),
                            ("under_review", "Under Review"),
                            ("needs_additional_review", "Needs Additional Review"),
                            ("rejected", "Rejected"),
                        ],
                        default="unverified",
                        max_length=50,
                    ),
                ),
                (
                    "contributor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "instrument",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hbs_entries",
                        to="instruments.instrument",
                    ),
                ),
            ],
        ),
        migrations.RunPython(
            migrate_strings_to_objects, reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="instrument",
            name="hornbostel_sachs_class",
            field=models.ForeignKey(
                blank=True,
                help_text="Currently selected Hornbostel–Sachs classification",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="main_for",
                to="instruments.hornbostelsachs",
            ),
        ),
    ]
