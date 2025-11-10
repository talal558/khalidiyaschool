from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("schoolaccounts.urls")),
    path("timetable/", include("schooltimetable.urls")),
    path("", include("schooldisplay.urls")),
]
