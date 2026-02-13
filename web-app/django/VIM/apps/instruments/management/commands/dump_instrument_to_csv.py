"""Management command that exports instrument names to a CSV file."""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from VIM.apps.instruments.models import InstrumentName


class Command(BaseCommand):
    """Dump every instrument name record to a CSV file."""

    help = "Exports instrument names from the database to a CSV file."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "-o",
            "--output",
            help="Destination CSV path. Defaults to dumped_csv/instrument_dump_<YYYY-MM-DD_HH-MM-SS>.csv.",
        )
        parser.add_argument(
            "--delimiter",
            default=",",
            help="Single-character delimiter to use (default: %(default)s).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite the output file if it already exists.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of rows to stream per batch while querying the database.",
        )

    def handle(self, *args, **options) -> None:
        delimiter: str = options["delimiter"]
        if len(delimiter) != 1:
            raise CommandError("Delimiter must be a single character.")

        batch_size: int = options["batch_size"]
        if batch_size < 1:
            raise CommandError("Batch size must be a positive integer.")

        timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_dir = Path("dumped_csv")
        default_filename = f"instrument_dump_{timestamp}.csv"

        if options["output"]:
            output_path = Path(options["output"]).expanduser().resolve()
        else:
            output_path = (default_dir / default_filename).expanduser().resolve()

        if output_path.exists() and not options["force"]:
            raise CommandError(
                f"{output_path} already exists. Use --force to overwrite the file."
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "instrument_name_id",
            "instrument_umil_id",
            "instrument_wikidata_id",
            "instrument_source",
            "language_wikidata_code",
            "language_en_label",
            "language_autonym",
            "name",
            "source_name",
            "verification_status",
            "umil_label",
            "contributor_username",
            "on_wikidata",
        ]

        queryset = (
            InstrumentName.objects.select_related(
                "instrument", "language", "contributor"
            )
            .order_by("instrument__umil_id", "language__wikidata_code", "name")
            .iterator(chunk_size=batch_size)
        )

        self.stdout.write(f"Writing instrument names to {output_path} ...")

        rows_written = 0
        with output_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            for instrument_name in queryset:
                instrument = instrument_name.instrument
                language = instrument_name.language
                contributor = instrument_name.contributor
                writer.writerow(
                    {
                        "instrument_name_id": instrument_name.id,
                        "instrument_umil_id": instrument.umil_id or "",
                        "instrument_wikidata_id": instrument.wikidata_id or "",
                        "instrument_source": instrument.source,
                        "language_wikidata_code": language.wikidata_code,
                        "language_en_label": language.en_label,
                        "language_autonym": language.autonym,
                        "name": instrument_name.name,
                        "source_name": instrument_name.source_name,
                        "verification_status": instrument_name.verification_status,
                        "umil_label": instrument_name.umil_label,
                        "contributor_username": contributor.username,
                        "on_wikidata": instrument_name.on_wikidata,
                    }
                )
                rows_written += 1

        if rows_written == 0:
            self.stdout.write(
                self.style.WARNING("No instrument names found. The CSV only has headers.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Export complete. {rows_written} instrument names written to {output_path}."
                )
            )
