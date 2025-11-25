# display/urls.py

from django.urls import path
from . import views

app_name = "schooldisplay"

urlpatterns = [
    # الصفحة الرئيسية: لوحة التوقيت المدرسي
    path("", views.dashboard, name="dashboard"),

    # صفحة لوحة التحكم
    path("control-panel/", views.control_panel, name="control_panel"),

    # صفحة لوحة التوقيت اليوم
    path("today-board/", views.today_board, name="today_board"),

    # API: جدول اليوم بصيغة JSON
    path("api/today-schedule/", views.api_today_schedule, name="api_today_schedule"),
]
