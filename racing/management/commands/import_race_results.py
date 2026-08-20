import json
from datetime import date
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from racing.models import (
    Circuit,
    DriverEntry,
    QualifyingResult,
    Race,
    RaceResult,
    Season,
)


class Command(BaseCommand):
    help = "Creates or updates one race and its qualifying and race results."

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
        circuit = self._upsert_circuit(data["circuit"])
        race = self._upsert_race(data, season, circuit)

        qualifying_count = self._upsert_qualifying_results(
            race=race,
            season=season,
            results=data.get("qualifying_results", []),
        )

        race_result_count = self._upsert_race_results(
            race=race,
            season=season,
            results=data.get("race_results", []),
        )

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
        required_fields = {
            "season",
            "round_number",
            "name",
            "race_date",
            "circuit",
        }

        missing = sorted(required_fields - data.keys())

        if missing:
            raise CommandError(
                f"Missing required top-level fields: {', '.join(missing)}"
            )

        if not isinstance(data["circuit"], dict):
            raise CommandError("'circuit' must be a JSON object.")

        circuit_required = {"name", "city", "country"}
        missing_circuit = sorted(circuit_required - data["circuit"].keys())

        if missing_circuit:
            raise CommandError(
                "Missing required circuit fields: " + ", ".join(missing_circuit)
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

    def _upsert_circuit(self, circuit_data: dict[str, Any]) -> Circuit:
        circuit, _ = Circuit.objects.update_or_create(
            name=circuit_data["name"],
            defaults={
                "city": circuit_data["city"],
                "country": circuit_data["country"],
            },
        )
        return circuit

    def _upsert_race(
        self,
        data: dict[str, Any],
        season: Season,
        circuit: Circuit,
    ) -> Race:
        try:
            race_date = date.fromisoformat(data["race_date"])
        except (TypeError, ValueError) as exc:
            raise CommandError("'race_date' must use YYYY-MM-DD format.") from exc

        race, _ = Race.objects.update_or_create(
            season=season,
            round_number=data["round_number"],
            defaults={
                "name": data["name"],
                "circuit": circuit,
                "race_date": race_date,
            },
        )
        return race

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
                    "laps_completed": result.get(
                        "laps_completed",
                        0,
                    ),
                    "total_time": result.get("total_time"),
                    "fastest_lap_time": result.get("fastest_lap_time"),
                    "fastest_lap_number": result.get("fastest_lap_number"),
                    "points": result.get("points", 0),
                    "status": result.get(
                        "status",
                        "Classified",
                    ),
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
            raise CommandError(f"Each {result_type} result must be a JSON object.")

        missing = sorted(required - result.keys())

        if missing:
            raise CommandError(
                f"Missing {result_type} result fields: " + ", ".join(missing)
            )
