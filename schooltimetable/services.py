import datetime
from django.utils import timezone
from .models import DaySchedule, SpecialDay

def _to_sa_weekday(date_obj):
    python_weekday = date_obj.weekday()  # Mon=0 .. Sun=6
    weekday_sa = (python_weekday + 1) % 7  # Sun -> 0
    return weekday_sa

def get_today_schedule(now=None):
    if now is None:
        now = timezone.localtime()

    today = now.date()
    special = (
        SpecialDay.objects.select_related("schedule")
        .filter(date=today, is_active=True)
        .first()
    )
    if special and special.schedule and special.schedule.is_active:
        return special.schedule

    weekday_sa = _to_sa_weekday(today)
    schedule = (
        DaySchedule.objects.filter(day_of_week=weekday_sa, is_active=True)
        .order_by("id")
        .first()
    )
    return schedule

def get_periods_with_state(schedule, now=None):
    if now is None:
        now = timezone.localtime()

    tz = timezone.get_current_timezone()
    periods_qs = schedule.periods.all().order_by("order", "start_time")

    periods_data = []
    current_index = None

    for idx, p in enumerate(periods_qs):
        start_naive = datetime.datetime.combine(now.date(), p.start_time)
        end_naive = datetime.datetime.combine(now.date(), p.end_time)

        start_dt = timezone.make_aware(start_naive, tz)
        end_dt = timezone.make_aware(end_naive, tz)

        if start_dt <= now <= end_dt:
            current_index = idx

        periods_data.append((p, start_dt, end_dt))

    return {"periods": periods_data, "current_index": current_index}
