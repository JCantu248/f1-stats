from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from racing.models import Constructor, Driver, DriverEntry, Race


@require_GET
def race_list(request):
    races = (
        Race.objects
        .select_related("season", "circuit")
        .order_by("season__year", "round_number")
    )

    data = [
        {
            "id": race.id,
            "season": race.season.year,
            "round_number": race.round_number,
            "name": race.name,
            "race_date": race.race_date.isoformat(),
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

    qualifying_results = (
        race.qualifying_results
        .select_related(
            "driver_entry__driver",
            "driver_entry__racecar__constructor",
        )
        .order_by("position")
    )

    race_results = (
        race.race_results
        .select_related(
            "driver_entry__driver",
            "driver_entry__racecar__constructor",
        )
        .order_by("finishing_position", "-laps_completed")
    )

    qualifying_data = [
        {
            "position": result.position,
            "driver": {
                "number": result.driver_entry.driver.permanent_number,
                "name": str(result.driver_entry.driver),
            },
            "constructor": (
                result.driver_entry.racecar.constructor.name
            ),
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
            "constructor": (
                result.driver_entry.racecar.constructor.name
            ),
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
            "circuit": {
                "name": race.circuit.name,
                "city": race.circuit.city,
                "country": race.circuit.country,
            },
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
        DriverEntry.objects
        .filter(racecar__constructor=constructor)
        .select_related(
            "driver",
            "racecar",
            "racecar__season",
            "racecar__constructor",
        )
        .order_by(
            "-racecar__season__year",
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
                "detail_url": (
                    f"/api/drivers/"
                    f"{entry.driver.permanent_number}/"
                ),
            },
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
            "detail_url": (
                f"/api/drivers/{driver.permanent_number}/"
            ),
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
        DriverEntry.objects
        .filter(driver=driver)
        .select_related(
            "racecar",
            "racecar__season",
            "racecar__constructor",
        )
        .order_by("-racecar__season__year")
    )

    entries = [
        {
            "season": entry.racecar.season.year,
            "constructor": {
                "id": entry.racecar.constructor.id,
                "name": entry.racecar.constructor.name,
                "detail_url": (
                    f"/api/constructors/"
                    f"{entry.racecar.constructor.id}/"
                ),
            },
            "racecar": str(entry.racecar),
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