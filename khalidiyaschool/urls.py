# khalidiyaschool/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # لوحة الإدارة
    path("admin/", admin.site.urls),

    # 👇 واجهة لوحة التوقيت (الصفحات: الرئيسية + لوحة التحكم)
    # نربط تطبيق display مع namespace = "schooldisplay"
    path(
        "",
        include(
            ("display.urls", "schooldisplay"),
            namespace="schooldisplay",
        ),
    ),

    # 👇 صفحات الحسابات (تسجيل الدخول / التسجيل)
    # نربط تطبيق schoolaccounts مع namespace = "schoolaccounts"
    path(
        "accounts/",
        include(
            ("schoolaccounts.urls", "schoolaccounts"),
            namespace="schoolaccounts",
        ),
    ),

    # 👇 ربط تطبيق التوقيت المدرسي (APIs الجدول اليومي، حصص المعلمين، إلخ)
    # تبقى على نفس المسارات الحالية مثل: /timetable/api/today-schedule/
    path(
        "",
        include(
            ("schooltimetable.urls", "schooltimetable"),
            namespace="schooltimetable",
        ),
    ),
]
