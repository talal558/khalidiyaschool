# display/views.py

from datetime import datetime

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import DaySchedule, Period


# ---------------------------------------------------------
#  دوال مساعدة
# ---------------------------------------------------------

def _get_today_weekday_code() -> int:
    """
    تحويل رقم يوم الأسبوع من تنسيق Django (الاثنين=0 .. الأحد=6)
    إلى تنسيق النظام الداخلي للجداول (السبت=0 .. الجمعة=6)
    """
    django_weekday = timezone.localdate().weekday()

    # الأحد = 6 في Django → السبت = 0 في النظام
    if django_weekday == 6:
        return 0

    return django_weekday + 1


def _build_aware_datetime(today, time_value):
    """
    دمج تاريخ اليوم مع وقت معين (وقت بداية أو نهاية الحصة)
    وتحويله إلى datetime مع WTZ.
    """
    dt = datetime.combine(today, time_value)
    return timezone.make_aware(dt, timezone.get_current_timezone())


# ---------------------------------------------------------
#  صفحات HTML
# ---------------------------------------------------------

def dashboard(request: HttpRequest) -> HttpResponse:
    """ الصفحة الرئيسية للوحة التحكم """
    return render(request, "display/dashboard.html")


def control_panel(request: HttpRequest) -> HttpResponse:
    """ لوحة التحكم (قابلة للتطوير لاحقاً) """
    return render(request, "display/control_panel.html")


def today_board(request: HttpRequest) -> HttpResponse:
    """
    صفحة (لوحة اليوم)
    - تعرض الساعة الحية
    - تعرض جدول اليوم
    - تُحدّد: الحصة الحالية / الحصص القادمة / المنتهية
    """

    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    # جلب الجدول النشط لليوم
    schedule = (
        DaySchedule.objects.filter(weekday=weekday_code, is_active=True)
        .order_by("id")
        .first()
    )

    if not schedule:
        return render(request, "display/today_board.html", {
            "today_lessons": [],
            "day_name": "—",
            "has_schedule": False,
        })

    periods_qs = (
        Period.objects.filter(schedule=schedule)
        .order_by("order", "start_time")
        .all()
    )

    now = timezone.localtime()

    periods = []
    current_period = None  # لتحديد الحصة الحالية في القالب

    for p in periods_qs:
        start_dt = _build_aware_datetime(today, p.start_time)
        end_dt = _build_aware_datetime(today, p.end_time)

        # تحديد حالة الحصة
        if end_dt <= now:
            status = "finished"
        elif start_dt <= now <= end_dt:
            status = "current"
            current_period = p
        else:
            status = "upcoming"

        periods.append({
            "id": p.id,
            "order": p.order,
            "name": p.name,
            "subject": p.subject,
            "teacher": p.teacher,
            "class_room": p.class_room,
            "type": p.type,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "status": status,
        })

    return render(request, "display/today_board.html", {
        "today_lessons": periods,
        "day_name": schedule.get_weekday_display(),
        "has_schedule": True,
        "current_period": current_period,
        "today_date": today,
    })


# ---------------------------------------------------------
#  API
# ---------------------------------------------------------

def api_today_schedule(request: HttpRequest) -> JsonResponse:
    """
    واجهة API:
    - ترجع جدول اليوم الكامل بصيغة JSON
    - تُستخدم للشاشات الرقمية و React و Vue وأي نظام خارجي
    """
    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    schedule = (
        DaySchedule.objects.filter(weekday=weekday_code, is_active=True)
        .order_by("id")
        .first()
    )

    if not schedule:
        return JsonResponse({
            "success": False,
            "message": "لا يوجد جدول معرف لهذا اليوم."
        })

    periods_qs = (
        Period.objects.filter(schedule=schedule)
        .order_by("order", "start_time")
        .all()
    )

    periods = []
    now = timezone.localtime()

    for p in periods_qs:
        start_dt = _build_aware_datetime(today, p.start_time)
        end_dt = _build_aware_datetime(today, p.end_time)

        if end_dt <= now:
            status = "finished"
        elif start_dt <= now <= end_dt:
            status = "current"
        else:
            status = "upcoming"

        periods.append({
            "id": p.id,
            "order": p.order,
            "name": p.name,
            "type": p.type,
            "subject": p.subject,
            "teacher": p.teacher,
            "class_room": p.class_room,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "status": status,
        })

    return JsonResponse({
        "success": True,
        "schedule": {
            "id": schedule.id,
            "weekday": schedule.weekday,
            "day_name": schedule.get_weekday_display(),
            "description": schedule.description,
        },
        "periods": periods,
    })
