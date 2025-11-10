from django.contrib import admin
from .models import DaySchedule, Period, SpecialDay

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
