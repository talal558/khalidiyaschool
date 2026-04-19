from __future__ import annotations

from datetime import datetime
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from schooltimetable.forms import (
    TeacherMainSlotForm, TeacherWaitingSlotForm, TeacherActivitySlotForm,
    DayScheduleForm, PeriodForm, SpecialDayForm,
)
from schooltimetable.models import (
    DaySchedule,
    DailyTimeSlot,
    Period,
    SpecialDay,
    Teacher,
    TeacherMainSlot,
    TeacherWaitingSlot,
    TeacherActivitySlot,
    DAYS_OF_WEEK,
)

User = get_user_model()


# ── Role helpers ─────────────────────────────────────────────────────────────

def _get_user_role(user) -> str:
    if user.is_superuser:
        return 'admin'
    try:
        return user.profile.role
    except Exception:
        return 'display'


def _require_role(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if _get_user_role(request.user) not in roles:
                messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
                return redirect('schooldisplay:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ── Auth helpers ─────────────────────────────────────────────────────────────

def _safe_next(request, url: str) -> str | None:
    """Return url only if it is a safe same-host relative URL."""
    if url and url_has_allowed_host_and_scheme(
        url=url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return url
    return None


def home(request):
    if request.user.is_authenticated:
        next_url = _safe_next(request, request.GET.get("next", ""))
        return redirect(next_url or "schooldisplay:dashboard")

    error = None
    raw_next = request.POST.get("next") or request.GET.get("next", "")
    next_url = _safe_next(request, raw_next)

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        if email and password:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect(next_url or "schooldisplay:dashboard")
            else:
                error = "البريد الإلكتروني أو كلمة المرور غير صحيحة."
        else:
            error = "يرجى ملء جميع الحقول."

    return render(request, "home.html", {"login_error": error, "next": next_url})


def _get_today_weekday_code() -> int:
    django_weekday = timezone.localdate().weekday()  # Monday=0 .. Sunday=6
    if django_weekday == 6:  # الأحد
        return 0
    return django_weekday + 1


def _build_aware_datetime(today, time_value):
    dt = datetime.combine(today, time_value)
    return timezone.make_aware(dt, timezone.get_current_timezone())


# ── Dashboard ────────────────────────────────────────────────────────────────

def dashboard(request):
    today = timezone.localdate()
    now = timezone.localtime()
    weekday_code = _get_today_weekday_code()

    today_weekday_label = dict(DAYS_OF_WEEK).get(weekday_code, "")
    today_date_str = today.strftime("%Y-%m-%d")

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
        "user_role": _get_user_role(request.user),
    }
    return render(request, "display/dashboard.html", context)


# ── Control Panel ────────────────────────────────────────────────────────────

@_require_role('admin', 'supervisor')
def control_panel(request):
    user_role = _get_user_role(request.user)
    context = {
        "page_title": "لوحة التحكم - مدرسة الخالدية الابتدائية",
        "slots_count":    TeacherMainSlot.objects.count(),
        "waiting_count":  TeacherWaitingSlot.objects.count(),
        "activity_count": TeacherActivitySlot.objects.count(),
        "teachers_count": Teacher.objects.count(),
        "schedules_count": DaySchedule.objects.count(),
        "periods_count":   Period.objects.count(),
        "class_periods_count": Period.objects.filter(period_type="class").count(),
        "special_days_count": SpecialDay.objects.filter(is_active=True).count(),
        "users_count":    User.objects.count(),
        "user_role": user_role,
    }
    return render(request, "display/control_panel.html", context)


# ── Teacher Slots ─────────────────────────────────────────────────────────────

@_require_role('admin', 'supervisor')
def teacher_main_slots(request):
    form = TeacherMainSlotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تمت إضافة المعلم إلى الحصة الرئيسية بنجاح.")
        return redirect("schooldisplay:teacher_main_slots")

    slots = TeacherMainSlot.objects.select_related("teacher").order_by("day_of_week", "start_time")
    return render(request, "display/teacher_main_slots.html", {"form": form, "slots": slots})


@_require_role('admin', 'supervisor')
def teacher_main_slot_delete(request, pk):
    slot = get_object_or_404(TeacherMainSlot, pk=pk)
    if request.method == "POST":
        slot.delete()
        messages.success(request, "تم حذف السجل بنجاح.")
    return redirect("schooldisplay:teacher_main_slots")


@_require_role('admin', 'supervisor')
def teacher_activity_slots(request):
    form = TeacherActivitySlotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تمت إضافة المعلم إلى حصص النشاط بنجاح.")
        return redirect("schooldisplay:teacher_activity_slots")

    slots = TeacherActivitySlot.objects.select_related("teacher").order_by("day_of_week", "start_time")
    return render(request, "display/teacher_activity_slots.html", {"form": form, "slots": slots})


@_require_role('admin', 'supervisor')
def teacher_activity_slot_delete(request, pk):
    slot = get_object_or_404(TeacherActivitySlot, pk=pk)
    if request.method == "POST":
        slot.delete()
        messages.success(request, "تم حذف السجل بنجاح.")
    return redirect("schooldisplay:teacher_activity_slots")


@_require_role('admin', 'supervisor')
def teacher_waiting_slots(request):
    form = TeacherWaitingSlotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تمت إضافة المعلم إلى قائمة الانتظار بنجاح.")
        return redirect("schooldisplay:teacher_waiting_slots")

    slots = TeacherWaitingSlot.objects.select_related("teacher").order_by("day_of_week", "start_time")
    return render(request, "display/teacher_waiting_slots.html", {"form": form, "slots": slots})


@_require_role('admin', 'supervisor')
def teacher_waiting_slot_delete(request, pk):
    slot = get_object_or_404(TeacherWaitingSlot, pk=pk)
    if request.method == "POST":
        slot.delete()
        messages.success(request, "تم حذف السجل بنجاح.")
    return redirect("schooldisplay:teacher_waiting_slots")


# ── Schedule Management ───────────────────────────────────────────────────────

@_require_role('admin', 'supervisor')
def schedule_list(request):
    form = DayScheduleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم إنشاء الجدول بنجاح.")
        return redirect("schooldisplay:schedule_list")

    schedules = (
        DaySchedule.objects
        .annotate(period_count=Count("periods"))
        .order_by("day_of_week", "id")
    )
    days_map = dict(DAYS_OF_WEEK)
    return render(request, "display/schedule_list.html", {
        "form": form,
        "schedules": schedules,
        "days_map": days_map,
    })


@_require_role('admin', 'supervisor')
def schedule_delete(request, pk):
    schedule = get_object_or_404(DaySchedule, pk=pk)
    if request.method == "POST":
        schedule.delete()
        messages.success(request, "تم حذف الجدول بنجاح.")
    return redirect("schooldisplay:schedule_list")


@_require_role('admin', 'supervisor')
def schedule_detail(request, pk):
    schedule = get_object_or_404(DaySchedule, pk=pk)
    form = PeriodForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        period = form.save(commit=False)
        period.schedule = schedule
        period.save()
        messages.success(request, "تمت إضافة الفترة بنجاح.")
        return redirect("schooldisplay:schedule_detail", pk=pk)

    periods = Period.objects.filter(schedule=schedule).order_by("order", "start_time")
    return render(request, "display/schedule_detail.html", {
        "schedule": schedule,
        "periods": periods,
        "form": form,
    })


@_require_role('admin', 'supervisor')
def period_delete(request, schedule_pk, pk):
    period = get_object_or_404(Period, pk=pk, schedule_id=schedule_pk)
    if request.method == "POST":
        period.delete()
        messages.success(request, "تم حذف الفترة بنجاح.")
    return redirect("schooldisplay:schedule_detail", pk=schedule_pk)


# ── Special Days ──────────────────────────────────────────────────────────────

@_require_role('admin', 'supervisor')
def special_days(request):
    form = SpecialDayForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تمت إضافة اليوم الخاص بنجاح.")
        return redirect("schooldisplay:special_days")

    days = SpecialDay.objects.select_related("schedule").order_by("-date")
    return render(request, "display/special_days.html", {"form": form, "days": days})


@_require_role('admin', 'supervisor')
def special_day_delete(request, pk):
    day = get_object_or_404(SpecialDay, pk=pk)
    if request.method == "POST":
        day.delete()
        messages.success(request, "تم حذف اليوم الخاص بنجاح.")
    return redirect("schooldisplay:special_days")


# ── Reports ───────────────────────────────────────────────────────────────────

@_require_role('admin', 'supervisor')
def reports(request):
    period_type_counts = {
        pt: Period.objects.filter(period_type=pt).count()
        for pt, _ in Period.PERIOD_TYPES
    }
    covered_periods  = Period.objects.exclude(teacher_name="").count()
    total_periods    = Period.objects.count()
    coverage_pct     = round(covered_periods / total_periods * 100) if total_periods else 0

    day_stats = []
    days_map = dict(DAYS_OF_WEEK)
    for code, name in DAYS_OF_WEEK:
        day_stats.append({
            "name": name,
            "schedules": DaySchedule.objects.filter(day_of_week=code).count(),
            "periods":   Period.objects.filter(schedule__day_of_week=code).count(),
            "main":      TeacherMainSlot.objects.filter(day_of_week=code).count(),
            "waiting":   TeacherWaitingSlot.objects.filter(day_of_week=code).count(),
            "activity":  TeacherActivitySlot.objects.filter(day_of_week=code).count(),
        })

    context = {
        "period_type_counts": period_type_counts,
        "period_type_labels": dict(Period.PERIOD_TYPES),
        "covered_periods":    covered_periods,
        "total_periods":      total_periods,
        "coverage_pct":       coverage_pct,
        "day_stats":          day_stats,
        "total_schedules":    DaySchedule.objects.count(),
        "active_schedules":   DaySchedule.objects.filter(is_active=True).count(),
        "total_teachers":     Teacher.objects.count(),
        "special_days_count": SpecialDay.objects.filter(is_active=True).count(),
    }
    return render(request, "display/reports.html", context)


# ── User Management ───────────────────────────────────────────────────────────

@_require_role('admin')
def user_management(request):
    from schoolaccounts.models import UserProfile

    all_users = User.objects.order_by("date_joined")
    user_list = []
    for u in all_users:
        try:
            role = u.profile.role
            role_display = u.profile.get_role_display()
        except Exception:
            role = 'display'
            role_display = 'عرض فقط'
        user_list.append({"user": u, "role": role, "role_display": role_display})

    return render(request, "display/user_management.html", {
        "user_list": user_list,
        "roles": UserProfile.ROLES,
    })


@_require_role('admin')
def user_role_update(request, user_id):
    from schoolaccounts.models import UserProfile

    target_user = get_object_or_404(User, pk=user_id)
    if target_user.is_superuser:
        messages.error(request, "لا يمكن تغيير صلاحية مستخدم السوبر يوزر.")
        return redirect("schooldisplay:user_management")
    if request.method == "POST":
        new_role = request.POST.get("role", "display")
        valid_roles = [r[0] for r in UserProfile.ROLES]
        if new_role in valid_roles:
            profile, _ = UserProfile.objects.get_or_create(user=target_user)
            profile.role = new_role
            profile.save()
            messages.success(request, f"تم تحديث صلاحية {target_user.username} بنجاح.")
        else:
            messages.error(request, "صلاحية غير صالحة.")
    return redirect("schooldisplay:user_management")


# ── Other views ───────────────────────────────────────────────────────────────

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
            "subject": p.subject or "",
            "teacher": p.teacher_name or "",
            "type": p.period_type,
            "start_time": p.start_time.strftime("%H:%M"),
            "end_time": p.end_time.strftime("%H:%M"),
            "status": status,
        })

    return render(request, "display/today_board.html", {
        "today_lessons": today_lessons,
        "day_name": dict(DAYS_OF_WEEK).get(weekday_code, "—"),
        "has_schedule": True,
        "current_period": current_period,
        "today_date": today,
    })
