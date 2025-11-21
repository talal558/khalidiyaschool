# display/urls.py
from django.urls import path
from . import views

app_name = "schooldisplay"

urlpatterns = [
    # الصفحة الرئيسية: لوحة التوقيت المدرسي (الواجهة)
    path("", views.dashboard, name="dashboard"),

    # صفحة لوحة التحكم (التي في header)
    path("control-panel/", views.control_panel, name="control_panel"),
]
