# display/urls.py
"""
مسارات تطبيق عرض لوحة التوقيت المدرسي (schooldisplay).
تحتوي على:
- الصفحة الرئيسية للوحة التوقيت
- لوحة التحكم
- لوحة اليوم (ساعة + جدول الحصص)
- واجهة API لجدول اليوم بصيغة JSON
"""

from django.urls import path
from . import views

app_name = "schooldisplay"

urlpatterns = [
    # الصفحة الرئيسية: لوحة التوقيت المدرسي
    path("", views.dashboard, name="dashboard"),

    # صفحة لوحة التحكم
    path("control-panel/", views.control_panel, name="control_panel"),

    # صفحة لوحة التوقيت اليوم (بطاقة الساعة + الجدول اليومي)
    path("today-board/", views.today_board, name="today_board"),

    # API: جدول اليوم بصيغة JSON (للشاشات أو الأنظمة الخارجية)
    path("api/today-schedule/", views.api_today_schedule, name="api_today_schedule"),
]
