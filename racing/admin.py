from django.contrib import admin

from .models import (
    Circuit,
    Constructor,
    Driver,
    DriverEntry,
    QualifyingResult,
    Race,
    Racecar,
    RaceResult,
    Season
)

admin.site.register(
    [
        Season,
        Constructor,
        Racecar,
        Driver,
        DriverEntry,
        Circuit,
        Race,
        QualifyingResult,
        RaceResult
    ]
)