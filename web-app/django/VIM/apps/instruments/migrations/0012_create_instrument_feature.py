import VIM.apps.instruments.models.avresource
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def populate_umil_ids(apps, schema_editor):
    """Assign sequential UMIL IDs (UMIL-00001 …) to every existing instrument.

    On production all instruments are Wikidata imports (Q-numbers);
    no user-created instruments exist at this point.
    """
    Instrument = apps.get_model("instruments", "Instrument")
    for num, instrument in enumerate(Instrument.objects.order_by("id"), start=1):
        instrument.umil_id = f"UMIL-{num:05d}"
        instrument.save(update_fields=["umil_id"])


def mark_existing_instruments_verified(apps, schema_editor):
    """Mark all pre-existing instruments as verified.

    Every instrument that exists before the create-instrument feature ships
    is a Wikidata import and should not land in the unverified queue.
    """
    Instrument = apps.get_model("instruments", "Instrument")
    Instrument.objects.all().update(verification_status="verified")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("instruments", "0011_language_html_direction"),
    ]

    operations = [
        # Instrument <-> AVResource have a circular FK (default_image, thumbnail,
        # and instrument). Django creates these as DEFERRABLE INITIALLY DEFERRED,
        # which queues constraint checks until COMMIT. PostgreSQL will not allow
        # ALTER TABLE while deferred checks are pending. Setting all constraints
        # to IMMEDIATE fires them now and keeps the migration fully atomic.
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name="avresource",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who uploaded this resource (null for imports)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_avresources",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="avresource",
            name="file",
            field=models.ImageField(
                blank=True,
                help_text="Uploaded image file",
                null=True,
                upload_to=VIM.apps.instruments.models.avresource.avresource_upload_path,
            ),
        ),
        migrations.AddField(
            model_name="instrument",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="When this instrument was created",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="instrument",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who created this instrument (null for Wikidata imports)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_instruments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="instrument",
            name="source",
            field=models.CharField(
                blank=True,
                help_text="Source/reference for this instrument entry",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="avresource",
            name="url",
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name="instrument",
            name="verification_status",
            field=models.CharField(
                choices=[
                    ("verified", "Verified"),
                    ("unverified", "Unverified"),
                    ("under_review", "Under Review"),
                    ("needs_additional_review", "Needs Additional Review"),
                    ("rejected", "Rejected"),
                ],
                default="unverified",
                help_text="Verification status of the instrument",
                max_length=50,
            ),
        ),
        migrations.RunPython(
            mark_existing_instruments_verified, migrations.RunPython.noop
        ),
        # umil_id: added nullable first, populated, then made unique+not-null.
        migrations.AddField(
            model_name="instrument",
            name="umil_id",
            field=models.CharField(
                blank=True,
                help_text="UMIL unique identifier (e.g., UMIL-00001)",
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(populate_umil_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="instrument",
            name="umil_id",
            field=models.CharField(
                help_text="UMIL unique identifier (e.g., UMIL-00001)",
                max_length=20,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="instrument",
            name="wikidata_id",
            field=models.CharField(
                blank=True,
                help_text="Wikidata Q-number (e.g., Q5994). Null for user-created instruments.",
                max_length=20,
                null=True,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="avresource",
            name="source_name",
            field=models.CharField(
                help_text="What is the name of the source of this AVResource?",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="instrument",
            name="needs_reindexing",
            field=models.BooleanField(
                default=False,
                help_text="True if Solr indexing failed and needs retry",
            ),
        ),
    ]
