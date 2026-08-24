from django.db.models import F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from racing.models import (
    Constructor,
    Driver,
    DriverEntry,
    Race,
    RaceResult,
    SprintResult,
)


@require_GET
def race_list(request):
    races = Race.objects.select_related("season", "circuit").order_by(
        "season__year", "race_date"
    )

    data = [
        {
            "id": race.id,
            "season": race.season.year,
            "round_number": race.round_number,
            "name": race.name,
            "race_date": race.race_date.isoformat(),
            "status": race.status,
            "status_note": race.status_note,
            "circuit": {
                "name": race.circuit.name,
                "city": race.circuit.city,
                "country": race.circuit.country,
            },
            "detail_url": f"/api/races/{race.id}/",
        }
        for race in races
    ]

    return JsonResponse(
        {
            "count": len(data),
            "results": data,
        }
    )


@require_GET
def race_detail(request, race_id):
    race = get_object_or_404(
        Race.objects.select_related("season", "circuit"),
        id=race_id,
    )

    sprint_qualifying_results = race.sprint_qualifying_results.select_related(
        "driver_entry__driver",
        "driver_entry__racecar__constructor",
    ).order_by(
        F("position").asc(nulls_last=True),
    )

    sprint_results = race.sprint_results.select_related(
        "driver_entry__driver",
        "driver_entry__racecar__constructor",
    ).order_by(
        F("finishing_position").asc(nulls_last=True),
        "-laps_completed",
    )

    qualifying_results = race.qualifying_results.select_related(
        "driver_entry__driver",
        "driver_entry__racecar__constructor",
    ).order_by(
        F("position").asc(nulls_last=True),
    )

    race_results = race.race_results.select_related(
        "driver_entry__driver",
        "driver_entry__racecar__constructor",
    ).order_by(
        F("finishing_position").asc(nulls_last=True),
        "-laps_completed",
    )

    sprint_qualifying_data = [
        {
            "position": result.position,
            "driver": {
                "number": result.driver_entry.driver.permanent_number,
                "name": str(result.driver_entry.driver),
            },
            "constructor": result.driver_entry.racecar.constructor.name,
            "q1_time": result.q1_time,
            "q2_time": result.q2_time,
            "q3_time": result.q3_time,
            "note": result.note,
        }
        for result in sprint_qualifying_results
    ]

    sprint_data = [
        {
            "finishing_position": result.finishing_position,
            "grid_position": result.grid_position,
            "driver": {
                "number": result.driver_entry.driver.permanent_number,
                "name": str(result.driver_entry.driver),
            },
            "constructor": result.driver_entry.racecar.constructor.name,
            "laps_completed": result.laps_completed,
            "total_time": result.total_time,
            "fastest_lap_time": result.fastest_lap_time,
            "fastest_lap_number": result.fastest_lap_number,
            "points": float(result.points),
            "status": result.status,
        }
        for result in sprint_results
    ]

    qualifying_data = [
        {
            "position": result.position,
            "driver": {
                "number": result.driver_entry.driver.permanent_number,
                "name": str(result.driver_entry.driver),
            },
            "constructor": result.driver_entry.racecar.constructor.name,
            "q1_time": result.q1_time,
            "q2_time": result.q2_time,
            "q3_time": result.q3_time,
            "note": result.note,
        }
        for result in qualifying_results
    ]

    race_data = [
        {
            "finishing_position": result.finishing_position,
            "grid_position": result.grid_position,
            "driver": {
                "number": result.driver_entry.driver.permanent_number,
                "name": str(result.driver_entry.driver),
            },
            "constructor": result.driver_entry.racecar.constructor.name,
            "laps_completed": result.laps_completed,
            "total_time": result.total_time,
            "fastest_lap_time": result.fastest_lap_time,
            "fastest_lap_number": result.fastest_lap_number,
            "points": float(result.points),
            "status": result.status,
        }
        for result in race_results
    ]

    return JsonResponse(
        {
            "id": race.id,
            "season": race.season.year,
            "round_number": race.round_number,
            "name": race.name,
            "race_date": race.race_date.isoformat(),
            "status": race.status,
            "status_note": race.status_note,
            "circuit": {
                "name": race.circuit.name,
                "city": race.circuit.city,
                "country": race.circuit.country,
            },
            "sprint_qualifying_results": sprint_qualifying_data,
            "sprint_results": sprint_data,
            "qualifying_results": qualifying_data,
            "race_results": race_data,
        }
    )


@require_GET
def constructor_list(request):
    constructors = Constructor.objects.order_by("name")

    results = [
        {
            "id": constructor.id,
            "name": constructor.name,
            "nation": constructor.nation,
            "detail_url": f"/api/constructors/{constructor.id}/",
        }
        for constructor in constructors
    ]

    return JsonResponse(
        {
            "count": len(results),
            "results": results,
        }
    )


@require_GET
def constructor_detail(request, constructor_id):
    constructor = get_object_or_404(
        Constructor,
        id=constructor_id,
    )

    driver_entries = (
        DriverEntry.objects.filter(racecar__constructor=constructor)
        .select_related(
            "driver",
            "racecar",
            "racecar__season",
            "racecar__constructor",
        )
        .order_by(
            "-racecar__season__year",
            "start_round",
            "driver__permanent_number",
        )
    )

    entries = [
        {
            "season": entry.racecar.season.year,
            "racecar": str(entry.racecar),
            "driver": {
                "id": entry.driver.id,
                "number": entry.driver.permanent_number,
                "name": str(entry.driver),
                "detail_url": (f"/api/drivers/{entry.driver.permanent_number}/"),
            },
            "start_round": entry.start_round,
            "end_round": entry.end_round,
        }
        for entry in driver_entries
    ]

    return JsonResponse(
        {
            "id": constructor.id,
            "name": constructor.name,
            "nation": constructor.nation,
            "entries": entries,
        }
    )


@require_GET
def driver_list(request):
    drivers = Driver.objects.order_by("permanent_number")

    results = [
        {
            "id": driver.id,
            "number": driver.permanent_number,
            "name": str(driver),
            "nationality": driver.nationality,
            "detail_url": f"/api/drivers/{driver.permanent_number}/",
        }
        for driver in drivers
    ]

    return JsonResponse(
        {
            "count": len(results),
            "results": results,
        }
    )


@require_GET
def driver_detail(request, driver_number):
    driver = get_object_or_404(
        Driver,
        permanent_number=driver_number,
    )

    season_entries = (
        DriverEntry.objects.filter(driver=driver)
        .select_related(
            "racecar",
            "racecar__season",
            "racecar__constructor",
        )
        .order_by("-racecar__season__year", "start_round")
    )

    entries = [
        {
            "season": entry.racecar.season.year,
            "constructor": {
                "id": entry.racecar.constructor.id,
                "name": entry.racecar.constructor.name,
                "detail_url": (f"/api/constructors/{entry.racecar.constructor.id}/"),
            },
            "racecar": str(entry.racecar),
            "start_round": entry.start_round,
            "end_round": entry.end_round,
        }
        for entry in season_entries
    ]

    return JsonResponse(
        {
            "id": driver.id,
            "number": driver.permanent_number,
            "name": str(driver),
            "nationality": driver.nationality,
            "entries": entries,
        }
    )


@require_GET
def driver_standings(request):
    season_year = 2026

    race_points = (
        RaceResult.objects.filter(race__season__year=season_year)
        .values(
            "driver_entry__driver__id",
            "driver_entry__driver__permanent_number",
            "driver_entry__driver__first_name",
            "driver_entry__driver__last_name",
            "driver_entry__driver__nationality",
        )
        .annotate(points=Sum("points"))
    )

    sprint_points = (
        SprintResult.objects.filter(race__season__year=season_year)
        .values(
            "driver_entry__driver__id",
        )
        .annotate(points=Sum("points"))
    )

    sprint_points_by_driver = {
        row["driver_entry__driver__id"]: row["points"] or 0 for row in sprint_points
    }

    standings = []

    for row in race_points:
        driver_id = row["driver_entry__driver__id"]

        total_points = (row["points"] or 0) + sprint_points_by_driver.get(driver_id, 0)

        standings.append(
            {
                "driver_id": driver_id,
                "number": row["driver_entry__driver__permanent_number"],
                "name": (
                    f"{row['driver_entry__driver__first_name']} "
                    f"{row['driver_entry__driver__last_name']}"
                ),
                "nationality": row["driver_entry__driver__nationality"],
                "points": float(total_points),
            }
        )

    standings.sort(
        key=lambda row: (
            -row["points"],
            row["name"],
        )
    )

    results = []

    for position, row in enumerate(
        standings,
        start=1,
    ):
        results.append(
            {
                "position": position,
                **row,
            }
        )

    return JsonResponse(
        {
            "season": season_year,
            "count": len(results),
            "results": results,
        }
    )


@require_GET
def constructor_standings(request):
    season_year = 2026

    race_points = (
        RaceResult.objects.filter(race__season__year=season_year)
        .values(
            "driver_entry__racecar__constructor__id",
            "driver_entry__racecar__constructor__name",
            "driver_entry__racecar__constructor__nation",
        )
        .annotate(points=Sum("points"))
    )

    sprint_points = (
        SprintResult.objects.filter(race__season__year=season_year)
        .values(
            "driver_entry__racecar__constructor__id",
        )
        .annotate(points=Sum("points"))
    )

    sprint_points_by_constructor = {
        row["driver_entry__racecar__constructor__id"]: row["points"] or 0
        for row in sprint_points
    }

    standings = []

    for row in race_points:
        constructor_id = row["driver_entry__racecar__constructor__id"]

        total_points = (row["points"] or 0) + sprint_points_by_constructor.get(
            constructor_id,
            0,
        )

        standings.append(
            {
                "constructor_id": constructor_id,
                "name": row["driver_entry__racecar__constructor__name"],
                "nation": row["driver_entry__racecar__constructor__nation"],
                "points": float(total_points),
            }
        )

    standings.sort(
        key=lambda row: (
            -row["points"],
            row["name"],
        )
    )

    results = []

    for position, row in enumerate(
        standings,
        start=1,
    ):
        results.append(
            {
                "position": position,
                **row,
            }
        )

    return JsonResponse(
        {
            "season": season_year,
            "count": len(results),
            "results": results,
        }
    )
