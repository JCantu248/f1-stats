import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from racing.models import (
    DriverEntry,
    QualifyingResult,
    Race,
    RaceResult,
    Season,
)


class Command(BaseCommand):
    help = "Imports qualifying and race results for an existing seeded race."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the race-results JSON file.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_path = Path(options["json_file"])

        if not json_path.is_file():
            raise CommandError(f"File does not exist: {json_path}")

        data = self._load_json(json_path)
        self._validate_document(data)

        season = self._get_season(data["season"])
        race = self._get_race(
            season=season,
            round_number=data["round_number"],
        )
        self._validate_race_identity(race, data)

        qualifying_count = self._upsert_qualifying_results(
            race=race,
            season=season,
            results=data.get("qualifying_results", []),
        )

        race_results = data.get("race_results", [])
        race_result_count = self._upsert_race_results(
            race=race,
            season=season,
            results=race_results,
        )

        if race_results:
            race.status = Race.Status.COMPLETED
            race.status_note = ""
            race.save(update_fields=["status", "status_note"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {race}: "
                f"{qualifying_count} qualifying results, "
                f"{race_result_count} race results."
            )
        )

    def _load_json(self, json_path: Path) -> dict[str, Any]:
        try:
            with json_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}") from exc
        except OSError as exc:
            raise CommandError(f"Could not read {json_path}: {exc}") from exc

        if not isinstance(data, dict):
            raise CommandError("The JSON root must be an object.")

        return data

    def _validate_document(self, data: dict[str, Any]) -> None:
        required_fields = {"season", "round_number"}
        missing = sorted(required_fields - data.keys())

        if missing:
            raise CommandError(
                f"Missing required top-level fields: {', '.join(missing)}"
            )

        for key in ("qualifying_results", "race_results"):
            value = data.get(key, [])

            if not isinstance(value, list):
                raise CommandError(f"'{key}' must be a JSON array.")

    def _get_season(self, year: int) -> Season:
        try:
            return Season.objects.get(year=year)
        except Season.DoesNotExist as exc:
            raise CommandError(
                f"Season {year} does not exist. Run seed_season first."
            ) from exc

    def _get_race(
        self,
        season: Season,
        round_number: int,
    ) -> Race:
        try:
            return Race.objects.select_related("circuit").get(
                season=season,
                round_number=round_number,
            )
        except Race.DoesNotExist as exc:
            raise CommandError(
                f"Round {round_number} for season {season.year} does not "
                "exist. Run seed_season first."
            ) from exc

    def _validate_race_identity(
        self,
        race: Race,
        data: dict[str, Any],
    ) -> None:
        supplied_name = data.get("name")

        if supplied_name and supplied_name != race.name:
            raise CommandError(
                f"Race file says '{supplied_name}', but season "
                f"{race.season.year} round {race.round_number} is "
                f"'{race.name}'."
            )

    def _get_driver_entry(
        self,
        season: Season,
        driver_number: int,
    ) -> DriverEntry:
        try:
            return DriverEntry.objects.select_related(
                "driver",
                "racecar",
                "racecar__season",
            ).get(
                racecar__season=season,
                driver__permanent_number=driver_number,
            )
        except DriverEntry.DoesNotExist as exc:
            raise CommandError(
                f"No driver entry found for car number "
                f"{driver_number} in season {season.year}."
            ) from exc
        except DriverEntry.MultipleObjectsReturned as exc:
            raise CommandError(
                f"Multiple driver entries found for car number "
                f"{driver_number} in season {season.year}."
            ) from exc

    def _upsert_qualifying_results(
        self,
        race: Race,
        season: Season,
        results: list[dict[str, Any]],
    ) -> int:
        count = 0

        for result in results:
            self._require_result_fields(
                result,
                required={"driver_number"},
                result_type="qualifying",
            )

            driver_entry = self._get_driver_entry(
                season=season,
                driver_number=result["driver_number"],
            )

            QualifyingResult.objects.update_or_create(
                race=race,
                driver_entry=driver_entry,
                defaults={
                    "position": result.get("position"),
                    "q1_time": result.get("q1_time"),
                    "q2_time": result.get("q2_time"),
                    "q3_time": result.get("q3_time"),
                    "note": result.get("note"),
                },
            )
            count += 1

        return count

    def _upsert_race_results(
        self,
        race: Race,
        season: Season,
        results: list[dict[str, Any]],
    ) -> int:
        count = 0

        for result in results:
            self._require_result_fields(
                result,
                required={"driver_number"},
                result_type="race",
            )

            driver_entry = self._get_driver_entry(
                season=season,
                driver_number=result["driver_number"],
            )

            RaceResult.objects.update_or_create(
                race=race,
                driver_entry=driver_entry,
                defaults={
                    "grid_position": result.get("grid_position"),
                    "finishing_position": result.get("finishing_position"),
                    "laps_completed": result.get("laps_completed", 0),
                    "total_time": result.get("total_time"),
                    "fastest_lap_time": result.get("fastest_lap_time"),
                    "fastest_lap_number": result.get("fastest_lap_number"),
                    "points": result.get("points", 0),
                    "status": result.get("status", "Classified"),
                },
            )
            count += 1

        return count

    def _require_result_fields(
        self,
        result: Any,
        required: set[str],
        result_type: str,
    ) -> None:
        if not isinstance(result, dict):
            raise CommandError(
                f"Each {result_type} result must be a JSON object."
            )

        missing = sorted(required - result.keys())

        if missing:
            raise CommandError(
                f"Missing {result_type} result fields: " + ", ".join(missing)
            )
