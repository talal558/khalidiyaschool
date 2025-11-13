from django.db import models
from django.conf import settings

DAYS_OF_WEEK = [
    (0, "الأحد"),
    (1, "الاثنين"),
    (2, "الثلاثاء"),
    (3, "الأربعاء"),
    (4, "الخميس"),
]

PERIOD_TYPES = [
    ("start", "بداية الدوام"),
    ("class", "حصة دراسية"),
    ("break", "فسحة / استراحة"),
    ("end", "نهاية الدوام"),
]

class DaySchedule(models.Model):
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_day_schedules",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="updated_day_schedules",
    )

    class Meta:
        ordering = ["day_of_week", "id"]
        verbose_name = "جدول يومي"
        verbose_name_plural = "الجداول اليومية"

    def __str__(self):
        name = dict(DAYS_OF_WEEK).get(self.day_of_week, str(self.day_of_week))
        if self.description:
            return f"{name} – {self.description}"
        return name


class Period(models.Model):
    schedule = models.ForeignKey(
        DaySchedule, on_delete=models.CASCADE, related_name="periods"
    )
    name = models.CharField(max_length=100)
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPES, default="class")
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_periods",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="updated_periods",
    )

    class Meta:
        ordering = ["order", "start_time"]
        verbose_name = "فترة"
        verbose_name_plural = "الفترات"

    def __str__(self):
        return f"{self.name} – {self.schedule}"


class SpecialDay(models.Model):
    date = models.DateField(unique=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    schedule = models.ForeignKey(
        DaySchedule, on_delete=models.SET_NULL, null=True, related_name="special_days"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_special_days",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="updated_special_days",
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = "يوم خاص"
        verbose_name_plural = "أيام خاصة"

    def __str__(self):
        return self.title or f"يوم خاص {self.date}"
from django.db import models


# لو عندك ثابت للأيام لا تكرره، لكن إن ما عندك استخدم هذا:
DAY_CHOICES = [
    (1, "الأحد"),
    (2, "الاثنين"),
    (3, "الثلاثاء"),
    (4, "الأربعاء"),
    (5, "الخميس"),
]


class Teacher(models.Model):
    """معلم في المدرسة"""
    name = models.CharField(max_length=150, verbose_name="اسم المعلم")
    code = models.CharField(
        max_length=20,
        verbose_name="الرمز (اختياري)",
        blank=True,
        unique=True,
        null=True,
    )

    class Meta:
        verbose_name = "معلم"
        verbose_name_plural = "المعلمون"
        ordering = ["name"]

    def __str__(self):
        return self.name if not self.code else f"{self.name} ({self.code})"


class BaseTeacherSlot(models.Model):
    """
    كلاس أساسي مشترك: يوم + وقت + معلم + ملاحظة
    ترث منه الجداول الثلاثة (عام / انتظار / نشاط)
    """
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        verbose_name="المعلم",
        related_name="%(class)s_slots",
    )
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        verbose_name="اليوم",
    )
    start_time = models.TimeField(verbose_name="من")
    end_time = models.TimeField(verbose_name="إلى")
    note = models.CharField(
        max_length=200,
        verbose_name="ملاحظات",
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return (
            f"{self.teacher} - {self.get_day_of_week_display()} "
            f"{self.start_time}–{self.end_time}"
        )


class TeacherMainSlot(BaseTeacherSlot):
    """حصة في الجدول العام للمعلم"""

    class Meta(BaseTeacherSlot.Meta):
        verbose_name = "حصة في الجدول العام"
        verbose_name_plural = "الجدول العام للمعلمين"


class TeacherWaitingSlot(BaseTeacherSlot):
    """حصة انتظار للمعلم"""

    class Meta(BaseTeacherSlot.Meta):
        verbose_name = "حصة انتظار للمعلم"
        verbose_name_plural = "جدول حصص الانتظار للمعلمين"


class TeacherActivitySlot(BaseTeacherSlot):
    """حصة نشاط للمعلم"""

    class Meta(BaseTeacherSlot.Meta):
        verbose_name = "حصة نشاط للمعلم"
        verbose_name_plural = "جدول حصص النشاط للمعلمين"
