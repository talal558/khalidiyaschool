from django.urls import path

from . import views

app_name = "schooldisplay"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("control-panel/", views.control_panel, name="control_panel"),
    path("school-year/", views.school_year_board, name="school_year_board"),
    path("today-board/", views.today_board, name="today_board"),
]
