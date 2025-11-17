from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # لوحة تحكم Django الافتراضية
    path("admin/", admin.site.urls),

    # الواجهة الرئيسية للمدرسة (شاشة العرض / لوحة التوقيت)
    # مثال: http://127.0.0.1:8000/
    path("", include("schooldisplay.urls")),

    # تطبيق الحسابات (تسجيل دخول، تسجيل، الخ...)
    # مثال: http://127.0.0.1:8000/accounts/...
    path("accounts/", include("schoolaccounts.urls")),

    # تطبيق الجداول (اليوم + انتظار + نشاط المعلمين + API)
    # مثال: http://127.0.0.1:8000/timetable/api/today-schedule/
    path("timetable/", include("schooltimetable.urls")),
]
