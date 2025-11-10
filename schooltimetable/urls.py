from django.urls import path
from . import views

urlpatterns = [
    path("api/today-schedule/", views.api_today_schedule, name="api_today_schedule"),
]
