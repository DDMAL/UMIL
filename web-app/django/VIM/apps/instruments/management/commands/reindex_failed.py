"""Management command to reindex instruments that failed initial indexing."""

import logging
from django.core.management.base import BaseCommand
from VIM.apps.instruments.models import Instrument
from VIM.apps.instruments.utils.solr_indexer import index_single_instrument

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reindex instruments that failed initial Solr indexing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be reindexed without actually doing it",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Find instruments needing reindexing
        failed_instruments = Instrument.objects.filter(needs_reindexing=True)
        count = failed_instruments.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No instruments need reindexing"))
            return

        self.stdout.write(f"Found {count} instrument(s) needing reindexing")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
            for instrument in failed_instruments:
                self.stdout.write(f"  - {instrument.umil_id} (ID: {instrument.pk})")
            return

        # Attempt to reindex each failed instrument
        success_count = 0
        still_failed = []

        for instrument in failed_instruments:
            self.stdout.write(
                f"Reindexing {instrument.umil_id} (ID: {instrument.pk})...", ending=" "
            )

            if index_single_instrument(instrument.pk):
                # Clear the flag on success
                instrument.needs_reindexing = False
                instrument.save(update_fields=["needs_reindexing"])
                success_count += 1
                self.stdout.write(self.style.SUCCESS("✓"))
            else:
                still_failed.append(instrument.umil_id)
                self.stdout.write(self.style.ERROR("✗ (still failing)"))

        # Summary
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully reindexed: {success_count}/{count}")
        )

        if still_failed:
            self.stdout.write(self.style.WARNING(f"Still failing: {len(still_failed)}"))
            for umil_id in still_failed:
                self.stdout.write(f"  - {umil_id}")
            self.stdout.write("")
            self.stdout.write("Check Solr service status and logs for details")
