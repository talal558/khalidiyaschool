# display/models.py
from django.db import models


class DaySchedule(models.Model):
    """
    جدول يومي واحد (مثلاً جدول يوم الأحد، الاثنين، ...).
    """

    WEEKDAY_CHOICES = [
        (0, "الأحد"),
        (1, "الاثنين"),
        (2, "الثلاثاء"),
        (3, "الأربعاء"),
        (4, "الخميس"),
        (5, "الجمعة"),
        (6, "السبت"),
    ]

    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        help_text="اختر اليوم الذي يطبق عليه هذا الجدول.",
    )
    description = models.CharField(
        max_length=100,
        default="جدول اليوم",
        help_text="وصف مختصر للجدول (مثلاً: جدول عادي، جدول اختبار، ...).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="تفعيل / تعطيل هذا الجدول.",
    )

    class Meta:
        verbose_name = "جدول يومي"
        verbose_name_plural = "الجداول اليومية"
        unique_together = ("weekday", "description")

    def __str__(self):
        return f"{self.get_weekday_display()} - {self.description}"


class Period(models.Model):
    """
    فترة واحدة داخل جدول اليوم (مثلاً: بداية الدوام، الحصة الأولى، فسحة، ...).
    """
    PERIOD_TYPE_CHOICES = [
        ("start", "بداية الدوام"),
        ("class", "حصة"),
        ("break", "فسحة"),
        ("end", "نهاية الدوام"),
        ("other", "فترة أخرى"),
    ]

    schedule = models.ForeignKey(
        DaySchedule,
        related_name="periods",
        on_delete=models.CASCADE,
        verbose_name="الجدول اليومي",
    )
    order = models.PositiveSmallIntegerField(
        verbose_name="الترتيب",
        help_text="ترتيب الفترة في الجدول (١، ٢، ٣، ...).",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="اسم الفترة",
        help_text="مثال: الحصة الأولى، بداية الدوام، فسحة...",
    )
    type = models.CharField(
        max_length=20,
        choices=PERIOD_TYPE_CHOICES,
        default="class",
        verbose_name="النوع",
    )
    start_time = models.TimeField(verbose_name="وقت البداية")
    end_time = models.TimeField(verbose_name="وقت النهاية")

    # معلومات إضافية اختيارية تظهر في الصفحة
    class_room = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="الفصل",
        help_text="مثال: الصف السادس (أ)",
    )
    teacher = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="المعلم",
    )
    subject = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="المادة",
    )

    class Meta:
        verbose_name = "فترة"
        verbose_name_plural = "الفترات"
        ordering = ["order"]

    def __str__(self):
        return f"{self.schedule} – {self.name}"
