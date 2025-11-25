# display/views.py

from datetime import datetime

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import DaySchedule, Period


def _get_today_weekday_code() -> int:
    """
    تحويل رقم يوم الأسبوع من تنسيق Django (الاثنين=0 .. الأحد=6)
    إلى تنسيق الجداول في النظام (السبت=0 .. الجمعة=6).
    """
    django_weekday = timezone.localdate().weekday()  # Monday=0 .. Sunday=6
    if django_weekday == 6:
        # في قاعدة البيانات: السبت = 0
        return 0
    return django_weekday + 1  # الأحد = 1 ... الجمعة = 6


def _build_aware_datetime(today, time_value):
    """
    دمج تاريخ اليوم مع وقت الحصة ثم تحويله إلى datetime
    مع وعي بالمنطقة الزمنية الحالية للمشروع.
    """
    dt = datetime.combine(today, time_value)
    return timezone.make_aware(dt, timezone.get_current_timezone())


def dashboard(request: HttpRequest) -> HttpResponse:
    """
    الصفحة الرئيسية للوحة التوقيت المدرسي.
    تعرض نظرة عامة وروابط للصفحات الأخرى.
    """
    return render(request, "display/dashboard.html")


def control_panel(request: HttpRequest) -> HttpResponse:
    """
    صفحة لوحة التحكم:
    سيتم لاحقًا إضافة إعدادات الجداول والفصول والمعلمين.
    """
    return render(request, "display/control_panel.html")


def today_board(request: HttpRequest) -> HttpResponse:
    """
    صفحة لوحة التوقيت اليوم:
    - تعرض الساعة الحية
    - جدول حصص اليوم
    - بطاقات الفصول

    حاليًا البيانات ثابتة في القالب، ويمكن ربطها لاحقًا
    ببيانات فعلية من قاعدة البيانات أو من API.
    """
    return render(request, "display/today_board.html")


def api_today_schedule(request: HttpRequest) -> JsonResponse:
    """
    API لقراءة جدول اليوم بصيغة JSON لاستخدامه في الواجهات أو الشاشات.

    تعيد:
    - بيانات الجدول النشط لليوم الحالي (إن وجد)
    - قائمة الفترات مع أوقات البداية والنهاية بتنسيق ISO.
    """
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
