# khalidiyaschool/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # لوحة الإدارة
    path("admin/", admin.site.urls),

    # مسار تسجيل الدخول الجاهز من Django
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),

    # مسار تسجيل الخروج
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="/"),
        name="logout",
    ),

    # API الجداول (schooltimetable)
    path("timetable/", include("schooltimetable.urls", namespace="schooltimetable")),

    # مسارات تطبيق schooldisplay (الصفحة الرئيسية للوحة التوقيت)
    # هذا يجعل / يوجه إلى schooldisplay.urls
    path("", include("schooldisplay.urls", namespace="schooldisplay")),
]
