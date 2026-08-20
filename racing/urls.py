from django.urls import path

from racing import views

app_name = "racing"

urlpatterns = [
    path("races/", views.race_list, name="race-list"),
    path("races/<int:race_id>/", views.race_detail, name="race-detail"),

    path(
        "constructors/",
        views.constructor_list,
        name="constructor-list",
    ),
    path(
        "constructors/<int:constructor_id>/",
        views.constructor_detail,
        name="constructor-detail",
    ),

    path("drivers/", views.driver_list, name="driver-list"),
    path(
        "drivers/<int:driver_number>/",
        views.driver_detail,
        name="driver-detail",
    ),
]