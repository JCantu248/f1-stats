import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from racing.models import (
    Constructor,
    Driver,
    DriverEntry,
    Racecar,
    Season,
)


class Command(BaseCommand):
    help = "Seeds the database from a season JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the season JSON file.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = Path(options["json_file"])

        if not json_file.exists():
            raise CommandError(f"File does not exist: {json_file}")

        try:
            with json_file.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
        except json.JSONDecodeError as ex:
            raise CommandError(f"Invalid JSON: {ex}")

        try:
            season, _ = Season.objects.get_or_create(
                year=data["season"]
            )

            self.stdout.write(
                self.style.SUCCESS(f"Loaded season {season.year}")
            )

            for constructor_data in data["constructors"]:

                constructor, _ = Constructor.objects.get_or_create(
                    name=constructor_data["name"],
                    defaults={
                        "nation": constructor_data["nation"],
                    },
                )

                racecar, _ = Racecar.objects.get_or_create(
                    season=season,
                    constructor=constructor,
                    defaults={
                        "chassis": constructor_data["racecar"]["chassis"],
                        "engine": constructor_data["racecar"]["engine"],
                    },
                )

                for driver_data in constructor_data["drivers"]:

                    driver, _ = Driver.objects.get_or_create(
                        permanent_number=driver_data["permanent_number"],
                        defaults={
                            "first_name": driver_data["first_name"],
                            "last_name": driver_data["last_name"],
                            "nationality": driver_data["nationality"],
                        },
                    )

                    DriverEntry.objects.get_or_create(
                        racecar=racecar,
                        driver=driver,
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    "Season imported successfully."
                )
            )

        except KeyError as ex:
            raise CommandError(
                f"Missing required field in JSON: {ex}"
            )