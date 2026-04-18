from django.contrib import admin

from .models import (
    Teacher,
    DailyTimeSlot,
    DaySchedule,
    Period,
    SpecialDay,
    TeacherMainSlot,
    TeacherWaitingSlot,
    TeacherActivitySlot,
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(DailyTimeSlot)
class DailyTimeSlotAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "period_number", "start_time", "end_time", "duration_minutes")
    list_filter = ("day_of_week",)
    ordering = ("day_of_week", "period_number")


@admin.register(DaySchedule)
class DayScheduleAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "is_active", "description")
    list_filter = ("day_of_week", "is_active")
    ordering = ("day_of_week", "id")


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ("schedule", "order", "name", "period_type", "start_time", "end_time", "subject", "teacher_name")
    list_filter = ("schedule", "period_type")
    ordering = ("schedule", "order")


@admin.register(SpecialDay)
class SpecialDayAdmin(admin.ModelAdmin):
    list_display = ("date", "schedule", "is_active", "note")
    list_filter = ("is_active",)
    ordering = ("date",)


@admin.register(TeacherMainSlot)
class TeacherMainSlotAdmin(admin.ModelAdmin):
    list_display = ("teacher", "day_of_week", "start_time", "end_time", "note")
    list_filter = ("day_of_week", "teacher")
    ordering = ("day_of_week", "start_time")


@admin.register(TeacherWaitingSlot)
class TeacherWaitingSlotAdmin(admin.ModelAdmin):
    list_display = ("teacher", "day_of_week", "start_time", "end_time", "note")
    list_filter = ("day_of_week", "teacher")
    ordering = ("day_of_week", "start_time")


@admin.register(TeacherActivitySlot)
class TeacherActivitySlotAdmin(admin.ModelAdmin):
    list_display = ("teacher", "day_of_week", "start_time", "end_time", "note")
    list_filter = ("day_of_week", "teacher")
    ordering = ("day_of_week", "start_time")
