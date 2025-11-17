from django.urls import path
from . import views

app_name = "schooldisplay"

urlpatterns = [
    # صفحات أخرى...
    path("school-year/", views.school_year_board, name="school_year_board"),
]
