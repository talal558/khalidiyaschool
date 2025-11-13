from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # لوحة التحكم الافتراضية لدجانغو
    path("admin/", admin.site.urls),

    # تطبيق عرض المدرسة / الواجهة الرئيسية
    path("", include("schooldisplay.urls")),

    # تطبيق الحسابات
    path("accounts/", include("schoolaccounts.urls")),

    # تطبيق الجداول (schooltimetable)
    path("timetable/", include("schooltimetable.urls")),
]
