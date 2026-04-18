from __future__ import annotations

from datetime import datetime

from django.shortcuts import render
from django.utils import timezone

from schooltimetable.models import (
    DaySchedule,
    Period,
    SpecialDay,
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
    أيام المدرسة، وعندها غالبًا لن يكون هناك جدول مفعّل.
    """
    django_weekday = timezone.localdate().weekday()  # Monday=0 .. Sunday=6

    if django_weekday == 6:  # الأحد
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


def dashboard(request):
    """
    صفحة لوحة التوقيت المدرسي (جدول اليوم):
    - تجيب DaySchedule المناسب لليوم (مع مراعاة SpecialDay إن وجد).
    - تجيب Period المرتبطة به.
    - تحسب حالة كل حصة (finished / current / upcoming).
    - ترسل البيانات إلى القالب display/dashboard.html.
    """

    today = timezone.localdate()
    now = timezone.localtime()
    weekday_code = _get_today_weekday_code()

    # اسم اليوم (من ثابت DAYS_OF_WEEK)
    today_weekday_label = dict(DAYS_OF_WEEK).get(weekday_code, "")
    # صيغة التاريخ الظاهرة تحت الساعة
    today_date_str = today.strftime("%Y-%m-%d")

    # 1) هل يوجد يوم خاص مفعّل اليوم؟
    special = (
        SpecialDay.objects.select_related("schedule")
        .filter(date=today, is_active=True, schedule__is_active=True)
        .first()
    )

    if special and special.schedule:
        schedule = special.schedule
    else:
        # 2) لو ما فيه يوم خاص: نستخدم الجدول العادي لليوم
        schedule = (
            DaySchedule.objects.filter(day_of_week=weekday_code, is_active=True)
            .order_by("id")
            .first()
        )

    today_lessons = []

    if schedule is not None:
        periods_qs = (
            Period.objects.filter(schedule=schedule)
            .order_by("order", "start_time")
            .all()
        )

        for index, p in enumerate(periods_qs, start=1):
            start_dt = _build_aware_datetime(today, p.start_time)
            end_dt = _build_aware_datetime(today, p.end_time)

            # حساب الحالة حسب الوقت الحالي
            if end_dt <= now:
                status = "finished"
            elif start_dt <= now <= end_dt:
                status = "current"
            else:
                status = "upcoming"

            # اسم المادة واسم المعلم (لو الحقول موجودة)
            subject = getattr(p, "subject", None) or getattr(p, "name", "")
            teacher_name = getattr(p, "teacher_name", None) or getattr(p, "teacher", None) or ""

            today_lessons.append(
                {
                    "order": getattr(p, "order", index),
                    "start_time": p.start_time,
                    "end_time": p.end_time,
                    "subject": subject,
                    "teacher_name": teacher_name,
                    "status": status,
                }
            )

    context = {
        "page_title": "لوحة التوقيت المدرسي - مدرسة الخالدية الابتدائية",
        "today_weekday": today_weekday_label,
        "today_date": today_date_str,
        "today_lessons": today_lessons,
    }

    return render(request, "display/dashboard.html", context)


def control_panel(request):
    """
    صفحة لوحة التحكم (يمكن تطويرها لاحقًا).
    """
    role = (
        "admin"
        if request.user.is_superuser
        else getattr(getattr(request.user, "profile", None), "role", "display")
    )
    if role not in ("admin", "supervisor"):
        from django.shortcuts import redirect
        return redirect("schooldisplay:dashboard")

    context = {
        "page_title": "لوحة التحكم - مدرسة الخالدية الابتدائية",
    }
    return render(request, "display/control_panel.html", context)


def school_year_board(request):
    """
    صفحة لوحة العام الدراسي (school_year_board).
    حاليًا صفحة بسيطة؛ يمكن تطويرها لاحقًا لعرض جدول السنة كاملة.
    """
    context = {
        "page_title": "لوحة العام الدراسي - مدرسة الخالدية الابتدائية",
    }
    return render(request, "display/school_year_board.html", context)
