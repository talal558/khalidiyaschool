from django.contrib import admin
from .models import (
    DaySchedule,
    Period,
    SpecialDay,
    Teacher,
    TeacherMainSlot,
    TeacherWaitingSlot,
    TeacherActivitySlot,
)


class PeriodInline(admin.TabularInline):
    model = Period
    extra = 1


@admin.register(DaySchedule)
class DayScheduleAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "description", "is_active")
    list_filter = ("day_of_week", "is_active")
    inlines = [PeriodInline]


@admin.register(SpecialDay)
class SpecialDayAdmin(admin.ModelAdmin):
    list_display = ("date", "title", "schedule", "is_active")
    list_filter = ("is_active",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


class BaseTeacherSlotAdmin(admin.ModelAdmin):
    list_display = ("teacher", "day_of_week", "start_time", "end_time", "note")
    list_filter = ("teacher", "day_of_week")
    search_fields = ("teacher__name", "note")


@admin.register(TeacherMainSlot)
class TeacherMainSlotAdmin(BaseTeacherSlotAdmin):
    pass


@admin.register(TeacherWaitingSlot)
class TeacherWaitingSlotAdmin(BaseTeacherSlotAdmin):
    pass


@admin.register(TeacherActivitySlot)
class TeacherActivitySlotAdmin(BaseTeacherSlotAdmin):
    pass
