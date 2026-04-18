# khalidiyaschool/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

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

    # مسار إنشاء حساب جديد
    path(
        "accounts/register/",
        CreateView.as_view(
            form_class=UserCreationForm,
            template_name="registration/register.html",
            success_url=reverse_lazy("login"),
        ),
        name="register",
    ),

    # API الجداول (schooltimetable)
    path("timetable/", include("schooltimetable.urls", namespace="schooltimetable")),

    # مسارات تطبيق schooldisplay (الصفحة الرئيسية للوحة التوقيت)
    # هذا يجعل / يوجه إلى schooldisplay.urls
    path("", include("schooldisplay.urls", namespace="schooldisplay")),
]
