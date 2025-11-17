from django.urls import path
from display import views as display_views  # نستخدم الفيوز من تطبيق display

app_name = "schooldisplay"  # عشان {% url 'schooldisplay:dashboard' %} تشتغل

urlpatterns = [
    # الرئيسية (لوحة التوقيت)
    path("", display_views.dashboard, name="dashboard"),

    # لوحة التحكم
    path("control-panel/", display_views.control_panel, name="control_panel"),

    # لوحة العام المدرسي
    path("school-year/", display_views.school_year_board, name="school_year_board"),
]
