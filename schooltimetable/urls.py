# schooltimetable/urls.py

from django.urls import path
from . import views

app_name = "schooltimetable"

urlpatterns = [
    # جدول اليوم العام (يستخدمه dashboard.html)
    path(
        "timetable/api/today-schedule/",
        views.api_today_schedule,
        name="api_today_schedule",
    ),

    # حصص الانتظار اليوم
    path(
        "timetable/api/teacher-waiting-slots/",
        views.api_teacher_waiting_slots,
        name="api_teacher_waiting_slots",
    ),

    # حصص النشاط اليوم
    path(
        "timetable/api/teacher-activity-slots/",
        views.api_teacher_activity_slots,
        name="api_teacher_activity_slots",
    ),

    # الجدول العام للمعلمين
    path(
        "timetable/api/teacher-main-slots/",
        views.api_teacher_main_slots,
        name="api_teacher_main_slots",
    ),
]
