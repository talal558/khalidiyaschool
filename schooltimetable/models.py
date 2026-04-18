from __future__ import annotations

from datetime import datetime, date
from django.db import models
from django.utils import timezone

# =========================
# ثوابت الأيام
# =========================
DAYS_OF_WEEK = [
    (0, "الأحد"),
    (1, "الاثنين"),
    (2, "الثلاثاء"),
    (3, "الأربعاء"),
    (4, "الخميس"),
]

# =========================
# المعلم
# =========================
class Teacher(models.Model):
    name = models.CharField("اسم المعلم", max_length=100)
    code = models.CharField("رمز المعلم", max_length=20, unique=True)

    class Meta:
        verbose_name = "معلم"
        verbose_name_plural = "المعلمين"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


# =========================
# جدول يوم
# =========================
class DaySchedule(models.Model):
    day_of_week = models.IntegerField("اليوم", choices=DAYS_OF_WEEK)
    description = models.CharField("وصف الجدول", max_length=255, blank=True)
    is_active = models.BooleanField("مفعل", default=True)

    class Meta:
        verbose_name = "جدول يوم"
        verbose_name_plural = "جداول الأيام"
        ordering = ["day_of_week", "id"]

    def __str__(self) -> str:
        return f"{self.get_day_of_week_display()} - {self.description or 'افتراضي'}"


# =========================
# فترات اليوم
# =========================
class Period(models.Model):
    PERIOD_TYPES = [
        ("class", "حصة دراسية"),
        ("break", "فسحة"),
        ("activity", "نشاط"),
        ("other", "أخرى"),
    ]

    schedule = models.ForeignKey(
        DaySchedule,
        on_delete=models.CASCADE,
        related_name="periods",
        verbose_name="الجدول اليومي",
    )
    order = models.PositiveSmallIntegerField("ترتيب الحصة")
    name = models.CharField("اسم الحصة", max_length=100)
    period_type = models.CharField(
        "نوع الفترة",
        max_length=20,
        choices=PERIOD_TYPES,
        default="class",
    )
    start_time = models.TimeField("وقت البداية")
    end_time = models.TimeField("وقت النهاية")
    subject = models.CharField("المادة", max_length=100, blank=True)
    teacher_name = models.CharField("اسم المعلم", max_length=100, blank=True)

    class Meta:
        ordering = ["schedule", "order"]
        unique_together = ("schedule", "order")

    def __str__(self):
        return self.name


# =========================
# يوم خاص
# =========================
class SpecialDay(models.Model):
    date = models.DateField("التاريخ", unique=True)
    schedule = models.ForeignKey(
        DaySchedule,
        on_delete=models.PROTECT,
        related_name="special_days",
        verbose_name="الجدول الخاص",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField("مفعل", default=True)
    note = models.CharField("ملاحظة", max_length=255, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return str(self.date)


# =========================
# قاعدة مشتركة لحصص المعلمين
# =========================
class BaseTeacherSlot(models.Model):
    day_of_week = models.IntegerField("اليوم", choices=DAYS_OF_WEEK)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_time = models.TimeField("وقت البداية")
    end_time = models.TimeField("وقت النهاية")
    note = models.CharField("ملاحظة", max_length=255, blank=True)

    class Meta:
        abstract = True


class TeacherMainSlot(BaseTeacherSlot):
    pass


class TeacherWaitingSlot(BaseTeacherSlot):
    pass


class TeacherActivitySlot(BaseTeacherSlot):
    pass


# =========================
# الفترات اليومية
# =========================
class DailyTimeSlot(models.Model):
    day_of_week = models.IntegerField("اليوم", choices=DAYS_OF_WEEK)
    period_number = models.PositiveSmallIntegerField("رقم الحصة")
    start_time = models.TimeField("وقت البداية")
    end_time = models.TimeField("وقت النهاية")

    class Meta:
        ordering = ["day_of_week", "period_number"]
        unique_together = ("day_of_week", "period_number")

    @property
    def duration_minutes(self) -> int:
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)
        return int((end_dt - start_dt).total_seconds() // 60)
