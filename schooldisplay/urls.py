from django.urls import path
from . import views

app_name = "schooldisplay"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # لوحة التحكم
    path("control-panel/", views.control_panel, name="control_panel"),

    # حصص المعلمين الرئيسية
    path("control-panel/teacher-slots/", views.teacher_main_slots, name="teacher_main_slots"),
    path("control-panel/teacher-slots/<int:pk>/delete/", views.teacher_main_slot_delete, name="teacher_main_slot_delete"),

    # قائمة الانتظار
    path("control-panel/waiting-slots/", views.teacher_waiting_slots, name="teacher_waiting_slots"),
    path("control-panel/waiting-slots/<int:pk>/delete/", views.teacher_waiting_slot_delete, name="teacher_waiting_slot_delete"),

    # حصص النشاط
    path("control-panel/activity-slots/", views.teacher_activity_slots, name="teacher_activity_slots"),
    path("control-panel/activity-slots/<int:pk>/delete/", views.teacher_activity_slot_delete, name="teacher_activity_slot_delete"),

    # إدارة الجداول اليومية
    path("control-panel/schedules/", views.schedule_list, name="schedule_list"),
    path("control-panel/schedules/<int:pk>/delete/", views.schedule_delete, name="schedule_delete"),
    path("control-panel/schedules/<int:pk>/", views.schedule_detail, name="schedule_detail"),
    path("control-panel/schedules/<int:schedule_pk>/periods/<int:pk>/delete/", views.period_delete, name="period_delete"),

    # الأيام الخاصة
    path("control-panel/special-days/", views.special_days, name="special_days"),
    path("control-panel/special-days/<int:pk>/delete/", views.special_day_delete, name="special_day_delete"),

    # التقارير
    path("control-panel/reports/", views.reports, name="reports"),

    # إدارة المستخدمين (مدير فقط)
    path("control-panel/users/", views.user_management, name="user_management"),
    path("control-panel/users/<int:user_id>/role/", views.user_role_update, name="user_role_update"),

    # صفحات العرض
    path("school-year/", views.school_year_board, name="school_year_board"),
    path("today-board/", views.today_board, name="today_board"),
]
