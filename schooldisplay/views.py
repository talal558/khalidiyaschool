from __future__ import annotations

from datetime import datetime

from django.shortcuts import render
from django.utils import timezone

from schooltimetable.models import (
    DaySchedule,
    DailyTimeSlot,
    Period,
    SpecialDay,
    DAYS_OF_WEEK,
)


def _get_today_weekday_code() -> int:
    django_weekday = timezone.localdate().weekday()  # Monday=0 .. Sunday=6
    if django_weekday == 6:  # الأحد
        return 0
    return django_weekday + 1


def _build_aware_datetime(today, time_value):
    dt = datetime.combine(today, time_value)
    return timezone.make_aware(dt, timezone.get_current_timezone())


def dashboard(request):
    today = timezone.localdate()
    now = timezone.localtime()
    weekday_code = _get_today_weekday_code()

    today_weekday_label = dict(DAYS_OF_WEEK).get(weekday_code, "")
    today_date_str = today.strftime("%Y-%m-%d")

    # هل يوجد يوم خاص مفعّل اليوم؟
    special = (
        SpecialDay.objects.select_related("schedule")
        .filter(date=today, is_active=True, schedule__is_active=True)
        .first()
    )

    schedule = special.schedule if (special and special.schedule) else (
        DaySchedule.objects.filter(day_of_week=weekday_code, is_active=True)
        .order_by("id")
        .first()
    )

    today_lessons = []
    if schedule is not None:
        for index, p in enumerate(
            Period.objects.filter(schedule=schedule).order_by("order", "start_time"),
            start=1,
        ):
            start_dt = _build_aware_datetime(today, p.start_time)
            end_dt = _build_aware_datetime(today, p.end_time)
            if end_dt <= now:
                status = "finished"
            elif start_dt <= now <= end_dt:
                status = "current"
            else:
                status = "upcoming"

            today_lessons.append({
                "order": p.order,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "subject": p.subject,
                "teacher_name": p.teacher_name,
                "status": status,
            })

    # بناء الجداول اليومية الزمنية من DailyTimeSlot
    all_slots = list(DailyTimeSlot.objects.order_by("day_of_week", "period_number"))
    daily_timetables = [
        {
            "name": day_name,
            "value": day_value,
            "slots": [s for s in all_slots if s.day_of_week == day_value],
        }
        for day_value, day_name in DAYS_OF_WEEK
    ]

    context = {
        "page_title": "لوحة التوقيت المدرسي - مدرسة الخالدية الابتدائية",
        "today_weekday": today_weekday_label,
        "today_date": today_date_str,
        "today_lessons": today_lessons,
        "daily_timetables": daily_timetables,
        "today_day_value": weekday_code,
    }
    return render(request, "display/dashboard.html", context)


def control_panel(request):
    context = {"page_title": "لوحة التحكم - مدرسة الخالدية الابتدائية"}
    return render(request, "display/control_panel.html", context)


def school_year_board(request):
    context = {"page_title": "لوحة العام الدراسي - مدرسة الخالدية الابتدائية"}
    return render(request, "display/school_year_board.html", context)


def today_board(request):
    today = timezone.localdate()
    now = timezone.localtime()
    weekday_code = _get_today_weekday_code()

    special = (
        SpecialDay.objects.select_related("schedule")
        .filter(date=today, is_active=True, schedule__is_active=True)
        .first()
    )

    schedule = special.schedule if (special and special.schedule) else (
        DaySchedule.objects.filter(day_of_week=weekday_code, is_active=True)
        .order_by("id")
        .first()
    )

    if schedule is None:
        return render(request, "display/today_board.html", {
            "today_lessons": [],
            "day_name": "—",
            "has_schedule": False,
            "today_date": today,
        })

    today_lessons = []
    current_period = None

    for p in Period.objects.filter(schedule=schedule).order_by("order", "start_time"):
        start_dt = _build_aware_datetime(today, p.start_time)
        end_dt = _build_aware_datetime(today, p.end_time)

        if end_dt <= now:
            status = "finished"
        elif start_dt <= now <= end_dt:
            status = "current"
            current_period = p
        else:
            status = "upcoming"

        today_lessons.append({
            "id": p.id,
            "order": p.order,
            "name": p.name,
            "subject": p.subject,
            "teacher": p.teacher_name,
            "class_room": "",
            "type": p.period_type,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "status": status,
        })

    return render(request, "display/today_board.html", {
        "today_lessons": today_lessons,
        "day_name": dict(DAYS_OF_WEEK).get(weekday_code, "—"),
        "has_schedule": True,
        "current_period": current_period,
        "today_date": today,
    })
