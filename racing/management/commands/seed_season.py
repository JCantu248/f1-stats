import json
from datetime import date
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from racing.models import (
    Circuit,
    Constructor,
    Driver,
    DriverEntry,
    Race,
    Racecar,
    Season,
)


class Command(BaseCommand):
    help = "Seeds a season, its entrants, and its full race calendar."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the season JSON file.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = Path(options["json_file"])

        if not json_file.is_file():
            raise CommandError(f"File does not exist: {json_file}")

        data = self._load_json(json_file)
        self._validate_document(data)

        season, _ = Season.objects.get_or_create(year=data["season"])
        self.stdout.write(self.style.SUCCESS(f"Loaded season {season.year}"))

        self._seed_constructors(season, data["constructors"])
        race_count = self._seed_calendar(season, data["races"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Season imported successfully with {race_count} calendar events."
            )
        )

    def _load_json(self, json_file: Path) -> dict[str, Any]:
        try:
            with json_file.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}") from exc
        except OSError as exc:
            raise CommandError(f"Could not read {json_file}: {exc}") from exc

        if not isinstance(data, dict):
            raise CommandError("The JSON root must be an object.")

        return data

    def _validate_document(self, data: dict[str, Any]) -> None:
        required = {"season", "constructors", "races"}
        missing = sorted(required - data.keys())

        if missing:
            raise CommandError(
                f"Missing required top-level fields: {', '.join(missing)}"
            )

        if not isinstance(data["constructors"], list):
            raise CommandError("'constructors' must be a JSON array.")

        if not isinstance(data["races"], list):
            raise CommandError("'races' must be a JSON array.")

    def _seed_constructors(
        self,
        season: Season,
        constructors: list[dict[str, Any]],
    ) -> None:
        for constructor_data in constructors:
            try:
                constructor, _ = Constructor.objects.update_or_create(
                    name=constructor_data["name"],
                    defaults={"nation": constructor_data["nation"]},
                )

                racecar, _ = Racecar.objects.update_or_create(
                    season=season,
                    constructor=constructor,
                    defaults={
                        "chassis": constructor_data["racecar"]["chassis"],
                        "engine": constructor_data["racecar"]["engine"],
                    },
                )

                for driver_data in constructor_data["drivers"]:
                    driver, _ = Driver.objects.update_or_create(
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
            except KeyError as exc:
                raise CommandError(
                    f"Missing required constructor/driver field: {exc}"
                ) from exc

    def _seed_calendar(
        self,
        season: Season,
        races: list[dict[str, Any]],
    ) -> int:
        count = 0

        for race_data in races:
            try:
                circuit_data = race_data["circuit"]
                race_date = date.fromisoformat(race_data["race_date"])
            except KeyError as exc:
                raise CommandError(
                    f"Missing required race field: {exc}"
                ) from exc
            except (TypeError, ValueError) as exc:
                raise CommandError(
                    "Race dates must use YYYY-MM-DD format."
                ) from exc

            status = race_data.get("status", Race.Status.SCHEDULED)
            valid_statuses = {choice.value for choice in Race.Status}

            if status not in valid_statuses:
                raise CommandError(
                    f"Invalid race status '{status}' for {race_data['name']}."
                )

            circuit, _ = Circuit.objects.update_or_create(
                name=circuit_data["name"],
                defaults={
                    "city": circuit_data["city"],
                    "country": circuit_data["country"],
                },
            )

            Race.objects.update_or_create(
                season=season,
                name=race_data["name"],
                defaults={
                    "round_number": race_data.get("round_number"),
                    "circuit": circuit,
                    "race_date": race_date,
                    "status": status,
                    "status_note": race_data.get("status_note", ""),
                },
            )
            count += 1

        return count
