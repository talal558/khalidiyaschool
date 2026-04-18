# schooltimetable/api_views.py
from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any

from django.http import JsonResponse, HttpRequest
from django.utils import timezone

from .models import (
    DaySchedule,
    Period,
    SpecialDay,
    TeacherMainSlot,
    TeacherWaitingSlot,
    TeacherActivitySlot,
    DAYS_OF_WEEK,
)


def _get_today_weekday_code() -> int:
    """
    يحوّل weekday تبع بايثون (الاثنين=0 .. الأحد=6)
    إلى كود أيام المدرسة في DAYS_OF_WEEK (الأحد=0 .. الخميس=4).

    Monday (0)  -> 1  (الاثنين)
    Tuesday (1) -> 2  (الثلاثاء)
    Wednesday(2)-> 3  (الأربعاء)
    Thursday (3)-> 4  (الخميس)
    Sunday (6)  -> 0  (الأحد)

    في حال كان اليوم جمعة (4) أو سبت (5)، يرجع قيمة خارج مدى
    أيام المدرسة، وعندها لن يجد جدولًا في قاعدة البيانات.
    """
    django_weekday = timezone.localdate().weekday()  # Monday=0 .. Sunday=6

    # إذا كان الأحد (6) نخليه 0 (الأحد)
    if django_weekday == 6:
        return 0

    # الباقي نحركه واحد (0->1، 1->2، 2->3، 3->4)
    return django_weekday + 1


def _build_aware_datetime(today, time_value):
    """
    يبني datetime (aware) باستخدام تاريخ اليوم + وقت معيّن،
    مع ربطه بالمنطقة الزمنية الحالية من إعدادات Django.
    """
    dt = datetime.combine(today, time_value)
    return timezone.make_aware(dt, timezone.get_current_timezone())


def _serialize_periods(queryset, today) -> List[Dict[str, Any]]:
    """
    يحوّل كائنات Period إلى قائمة قواميس جاهزة للإرسال كـ JSON.
    """
    periods: List[Dict[str, Any]] = []

    for p in queryset:
        start_dt = _build_aware_datetime(today, p.start_time)
        end_dt = _build_aware_datetime(today, p.end_time)

        periods.append(
            {
                "id": p.id,
                "name": p.name,
                "type": p.period_type,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
            }
        )

    return periods


def _serialize_teacher_slots(queryset, today) -> List[Dict[str, Any]]:
    """
    يحوّل كائنات Teacher*Slot إلى قائمة قواميس موحّدة:
    (مستخدمة في حصص الانتظار، النشاط، والجدول العام).
    """
    slots: List[Dict[str, Any]] = []

    for s in queryset:
        start_dt = _build_aware_datetime(today, s.start_time)
        end_dt = _build_aware_datetime(today, s.end_time)

        slots.append(
            {
                "id": s.id,
                "teacher_name": s.teacher.name,
                "teacher_code": s.teacher.code,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "note": s.note or "",
            }
        )

    return slots


# =========================
#  API: جدول اليوم العام
# =========================


def api_today_schedule(request: HttpRequest) -> JsonResponse:
    """
    يرجع جدول اليوم (DaySchedule + Periods) بناءً على اليوم الحالي،
    مع مراعاة SpecialDay إن وجد.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "يجب تسجيل الدخول أولاً."}, status=401)

    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "طريقة الطلب غير مدعومة. استخدم GET فقط.",
            },
            status=405,
        )

    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    # لو فيه يوم خاص في SpecialDay نستخدم جدوله
    special = (
        SpecialDay.objects.select_related("schedule")
        .filter(date=today, is_active=True, schedule__is_active=True)
        .first()
    )

    if special and special.schedule:
        schedule = special.schedule
    else:
        schedule = (
            DaySchedule.objects.filter(day_of_week=weekday_code, is_active=True)
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

    day_name = dict(DAYS_OF_WEEK).get(schedule.day_of_week, str(schedule.day_of_week))

    periods_qs = (
        Period.objects.filter(schedule=schedule)
        .order_by("order", "start_time")
        .all()
    )

    periods = _serialize_periods(periods_qs, today)

    return JsonResponse(
        {
            "success": True,
            "schedule": {
                "id": schedule.id,
                "day": schedule.day_of_week,
                "day_name": day_name,
                "description": schedule.description,
            },
            "periods": periods,
        }
    )


# =========================
#  API: حصص الانتظار اليوم
# =========================


def api_teacher_waiting_slots(request: HttpRequest) -> JsonResponse:
    """
    يرجع حصص الانتظار للمعلمين لليوم الحالي (TeacherWaitingSlot).
    """
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "يجب تسجيل الدخول أولاً."}, status=401)

    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "طريقة الطلب غير مدعومة. استخدم GET فقط.",
            },
            status=405,
        )

    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    slots_qs = (
        TeacherWaitingSlot.objects.select_related("teacher")
        .filter(day_of_week=weekday_code)
        .order_by("start_time")
    )

    slots = _serialize_teacher_slots(slots_qs, today)

    if not slots:
        return JsonResponse(
            {
                "success": False,
                "message": "لا توجد حصص انتظار للمعلمين لليوم الحالي.",
                "slots": [],
            }
        )

    return JsonResponse({"success": True, "slots": slots})


# =========================
#  API: حصص النشاط اليوم
# =========================


def api_teacher_activity_slots(request: HttpRequest) -> JsonResponse:
    """
    يرجع حصص النشاط للمعلمين لليوم الحالي (TeacherActivitySlot).
    """
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "يجب تسجيل الدخول أولاً."}, status=401)

    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "طريقة الطلب غير مدعومة. استخدم GET فقط.",
            },
            status=405,
        )

    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    slots_qs = (
        TeacherActivitySlot.objects.select_related("teacher")
        .filter(day_of_week=weekday_code)
        .order_by("start_time")
    )

    slots = _serialize_teacher_slots(slots_qs, today)

    if not slots:
        return JsonResponse(
            {
                "success": False,
                "message": "لا توجد حصص نشاط للمعلمين لليوم الحالي.",
                "slots": [],
            }
        )

    return JsonResponse({"success": True, "slots": slots})


# =========================
#  API: الجدول العام للمعلمين (لوحة التحكم)
# =========================


def api_teacher_main_slots(request: HttpRequest) -> JsonResponse:
    """
    يرجع حصص الجدول العام للمعلمين لليوم الحالي (TeacherMainSlot)
    لاستخدامها في صفحة لوحة التحكم.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "يجب تسجيل الدخول أولاً."}, status=401)

    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "طريقة الطلب غير مدعومة. استخدم GET فقط.",
            },
            status=405,
        )

    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    slots_qs = (
        TeacherMainSlot.objects.select_related("teacher")
        .filter(day_of_week=weekday_code)
        .order_by("start_time", "teacher__name")
    )

    slots = _serialize_teacher_slots(slots_qs, today)

    if not slots:
        return JsonResponse(
            {
                "success": False,
                "message": "لا توجد حصص في الجدول العام للمعلمين لليوم الحالي.",
                "slots": [],
            }
        )

    return JsonResponse({"success": True, "slots": slots})
