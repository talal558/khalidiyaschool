from datetime import datetime

from django.http import JsonResponse
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
    تحويل weekday تبع بايثون (الاثنين=0 .. الأحد=6)
    إلى كود DAYS_OF_WEEK (الأحد=0 .. الخميس=4).
    """
    django_weekday = timezone.localdate().weekday()  # Monday=0 .. Sunday=6

    # إذا كان الأحد (6) نخليه 0، والباقي نحركه واحد
    if django_weekday == 6:
        return 0
    return django_weekday + 1


def _build_aware_datetime(today, time_value):
    """
    يبني datetime aware (مع المنطقة الزمنية الحالية)
    من تاريخ اليوم + وقت معين.
    """
    dt = datetime.combine(today, time_value)
    return timezone.make_aware(dt, timezone.get_current_timezone())


# =========================
#  API: جدول اليوم العام
# =========================

def api_today_schedule(request):
    """
    يرجع جدول اليوم (DaySchedule + Periods) بناءً على اليوم الحالي
    مع مراعاة SpecialDay إن وجد.
    الاستجابة متوافقة مع JavaScript في dashboard.html:
    {
        "success": True/False,
        "message": "...",        # في حالة عدم النجاح
        "schedule": {
            "id": ...,
            "day": ...,
            "day_name": "...",
            "description": "...",
        },
        "periods": [
            {
                "id": ...,
                "name": "...",
                "type": "...",
                "start": "ISO datetime",
                "end": "ISO datetime",
            },
            ...
        ]
    }
    """
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

    periods = []
    for p in periods_qs:
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

def api_teacher_waiting_slots(request):
    """
    يرجع حصص الانتظار للمعلمين لليوم الحالي (TeacherWaitingSlot).
    """
    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    slots_qs = (
        TeacherWaitingSlot.objects.select_related("teacher")
        .filter(day_of_week=weekday_code)
        .order_by("start_time")
    )

    slots = []
    for s in slots_qs:
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

def api_teacher_activity_slots(request):
    """
    يرجع حصص النشاط للمعلمين لليوم الحالي (TeacherActivitySlot).
    """
    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    slots_qs = (
        TeacherActivitySlot.objects.select_related("teacher")
        .filter(day_of_week=weekday_code)
        .order_by("start_time")
    )

    slots = []
    for s in slots_qs:
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

def api_teacher_main_slots(request):
    """
    يرجع حصص الجدول العام للمعلمين لليوم الحالي (TeacherMainSlot)
    لاستخدامها في صفحة لوحة التحكم:
    - اسم المعلم
    - الرمز
    - من / إلى
    - ملاحظات
    """
    today = timezone.localdate()
    weekday_code = _get_today_weekday_code()

    slots_qs = (
        TeacherMainSlot.objects.select_related("teacher")
        .filter(day_of_week=weekday_code)
        .order_by("start_time", "teacher__name")
    )

    slots = []
    for s in slots_qs:
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

    if not slots:
        return JsonResponse(
            {
                "success": False,
                "message": "لا توجد حصص في الجدول العام للمعلمين لليوم الحالي.",
                "slots": [],
            }
        )

    return JsonResponse({"success": True, "slots": slots})
