from django.urls import path

from . import views

app_name = "schooltimetable"

urlpatterns = [
    path("api/today-schedule/", views.api_today_schedule, name="api_today_schedule"),
    path(
        "api/teacher-waiting-slots/",
        views.api_teacher_waiting_slots,
        name="api_teacher_waiting_slots",
    ),
    path(
        "api/teacher-activity-slots/",
        views.api_teacher_activity_slots,
        name="api_teacher_activity_slots",
    ),
    path(
        "api/teacher-main-slots/",
        views.api_teacher_main_slots,
        name="api_teacher_main_slots",
    ),
]
