from django.db import models


class Season(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return str(self.year)


class Constructor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    nation = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Racecar(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="racecars")
    constructor = models.ForeignKey(Constructor, on_delete=models.CASCADE, related_name="racecars")
    chassis = models.CharField(max_length=100)
    engine = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["season", "constructor"],
                name="unique_constructor_car_per_season",
            )
        ]

    def __str__(self):
        return f"{self.season} {self.constructor} {self.chassis}"


class Driver(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    permanent_number = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class DriverEntry(models.Model):
    racecar = models.ForeignKey(Racecar, on_delete=models.CASCADE, related_name="driver_entries")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="season_entries")

    def __str__(self):
        return f"{self.driver} - {self.racecar}"


class Circuit(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Race(models.Model):
    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE, 
        related_name="races"
    )
    round_number = models.PositiveIntegerField()
    name = models.CharField(max_length=150)
    circuit = models.ForeignKey(
        Circuit, 
        on_delete=models.CASCADE, 
        related_name="races"
    )
    race_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["season", "round_number"],
                name="unique_round_per_season",
            ),
            models.UniqueConstraint(
                fields=["season", "name"],
                name="unique_race_name_per_season"
            )
        ]
        ordering = ["season", "round_number"]

    def __str__(self):
        return f"{self.season.year} {self.name}"

class QualifyingResult(models.Model):
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name="qualifying_results",
    )
    driver_entry = models.ForeignKey(
        DriverEntry,
        on_delete=models.CASCADE,
        related_name="qualifying_results",
    )
    position = models.PositiveIntegerField(null=True, blank=True)
    q1_time = models.CharField(max_length=20, null=True, blank=True)
    q2_time = models.CharField(max_length=20, null=True, blank=True)
    q3_time = models.CharField(max_length=20, null=True, blank=True)
    note = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["race", "driver_entry"],
                name="unique_driver_qualifying_result_per_race",
            ),
            models.UniqueConstraint(
                fields=["race", "position"],
                name="unique_qualifying_position_per_race",
                condition=models.Q(position__isnull=False),
            ),
        ]
        ordering = ["position"]

    def __str__(self):
        return (
            f"{self.race} qualifying - "
            f"{self.driver_entry.driver}"
        )


class RaceResult(models.Model):
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name="race_results",
    )
    driver_entry = models.ForeignKey(
        DriverEntry,
        on_delete=models.CASCADE,
        related_name="race_results",
    )
    grid_position = models.PositiveIntegerField(null=True, blank=True)
    finishing_position = models.PositiveIntegerField(null=True, blank=True)
    laps_completed = models.PositiveIntegerField(default=0)
    total_time = models.CharField(max_length=50, null=True, blank=True)
    fastest_lap_time = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    fastest_lap_number = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    status = models.CharField(max_length=100, default="Classified")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["race", "driver_entry"],
                name="unique_driver_race_result_per_race",
            ),
            models.UniqueConstraint(
                fields=["race", "finishing_position"],
                name="unique_finishing_position_per_race",
                condition=models.Q(finishing_position__isnull=False),
            ),
        ]
        ordering = ["finishing_position"]

    def __str__(self):
        return (
            f"{self.race} result - "
            f"{self.driver_entry.driver}"
        )

