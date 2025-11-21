# display/views.py
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import DaySchedule, Period


def _get_today_weekday_code() -> int:
    django_weekday = timezone.localdate().weekday()  # Monday=0 .. Sunday=6
    if django_weekday == 6:
        return 0
    return django_weekday + 1


def _build_aware_datetime(today, time_value):
    dt = datetime.combine(today, time_value)
    return timezone.make_aware(dt, timezone.get_current_timezone())


# صفحة لوحة التوقيت (الرئيسية)
def dashboard(request):
    return render(request, "display/dashboard.html")


# API جدول اليوم
def api_today_schedule(request):
    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    schedule = (
        DaySchedule.objects.filter(weekday=weekday_code, is_active=True)
        .order_by("id")
        .first()
    )

    if not schedule:
        return JsonResponse(
            {
                "success": False,
                "message": "لا يوجد جدول معرف لهذا اليوم في قاعدة البيانات.",
            }
        )

    day_name = schedule.get_weekday_display()

    periods_qs = (
        Period.objects.filter(schedule=schedule)
        .order_by("order", "start_time")
        .all()
    )

    periods = []
    for p in periods_qs:
        start_dt = _build_aware_datetime(today, p.start_time)
        end_dt = _build_aware_datetime(today, p.end_time)

        periods.append(
            {
                "id": p.id,
                "name": p.name,
                "type": p.type,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "class_room": p.class_room,
                "teacher": p.teacher,
                "subject": p.subject,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "schedule": {
                "id": schedule.id,
                "weekday": schedule.weekday,
                "day_name": day_name,
                "description": schedule.description,
            },
            "periods": periods,
        }
    )


# ✅ صفحة لوحة التحكم (المطلوبة في الهيدر)
def control_panel(request):
    return render(request, "display/control_panel.html")
