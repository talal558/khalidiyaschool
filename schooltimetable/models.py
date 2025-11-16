from django.db import models
from django.conf import settings

# ثوابت الأيام (تُستخدم في كل الجداول)
DAYS_OF_WEEK = [
    (0, "الأحد"),
    (1, "الاثنين"),
    (2, "الثلاثاء"),
    (3, "الأربعاء"),
    (4, "الخميس"),
]

# أنواع الفترات في اليوم الدراسي
PERIOD_TYPES = [
    ("start", "بداية الدوام"),
    ("class", "حصة دراسية",
    ),
    ("break", "فسحة / استراحة"),
    ("end", "نهاية الدوام"),
]


class DaySchedule(models.Model):
    """
    جدول أساسي ليوم معين (أحد / اثنين ...)،
    يُربط به الفترات (Period) ويُستخدم كجدول افتراضي لليوم.
    """

    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name="اليوم",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="وصف الجدول",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="مفعل",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ آخر تعديل",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_day_schedules",
        verbose_name="أُنشئ بواسطة",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_day_schedules",
        verbose_name="عُدّل بواسطة",
    )

    class Meta:
        ordering = ["day_of_week", "id"]
        verbose_name = "جدول يومي"
        verbose_name_plural = "الجداول اليومية"
        constraints = [
            models.UniqueConstraint(
                fields=["day_of_week", "description"],
                name="unique_day_schedule_per_description",
            ),
        ]

    def __str__(self):
        name = dict(DAYS_OF_WEEK).get(self.day_of_week, str(self.day_of_week))
        if self.description:
            return f"{name} – {self.description}"
        return name


class Period(models.Model):
    """
    فترة زمنية ضمن جدول يومي معيّن
    (حصة، فسحة، بداية الدوام، نهاية الدوام...).
    """

    schedule = models.ForeignKey(
        DaySchedule,
        on_delete=models.CASCADE,
        related_name="periods",
        verbose_name="الجدول اليومي",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="اسم الفترة",
    )
    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_TYPES,
        default="class",
        verbose_name="نوع الفترة",
    )
    start_time = models.TimeField(
        verbose_name="وقت البداية",
    )
    end_time = models.TimeField(
        verbose_name="وقت النهاية",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="ترتيب الفترة",
        help_text="الترتيب داخل اليوم (1 للحصة الأولى، 2 للثانية، ...).",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ آخر تعديل",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_periods",
        verbose_name="أُنشئت بواسطة",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_periods",
        verbose_name="عُدّلت بواسطة",
    )

    class Meta:
        ordering = ["order", "start_time"]
        verbose_name = "فترة"
        verbose_name_plural = "الفترات"
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "order"],
                name="unique_period_order_per_schedule",
            ),
        ]

    def __str__(self):
        return f"{self.name} – {self.schedule}"


class SpecialDay(models.Model):
    """
    يوم خاص: (اختبار، فعالية، دوام مختلف ...)،
    يربط تاريخ معيّن بجدول يومي موجود.
    """

    date = models.DateField(
        unique=True,
        verbose_name="التاريخ",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="عنوان اليوم الخاص",
    )
    schedule = models.ForeignKey(
        DaySchedule,
        on_delete=models.SET_NULL,
        null=True,
        related_name="special_days",
        verbose_name="الجدول المستخدم في هذا اليوم",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="مفعل",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاريخ آخر تعديل",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_special_days",
        verbose_name="أُنشئ بواسطة",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_special_days",
        verbose_name="عُدّل بواسطة",
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = "يوم خاص"
        verbose_name_plural = "أيام خاصة"

    def __str__(self):
        return self.title or f"يوم خاص {self.date}"


# =========================
#  جـــــدول المعلمين
# =========================

class Teacher(models.Model):
    """معلم في المدرسة"""

    name = models.CharField(
        max_length=150,
        verbose_name="اسم المعلم",
    )
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
    ترث منه الجداول الثلاثة (عام / انتظار / نشاط).
    """

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        verbose_name="المعلم",
        related_name="%(class)s_slots",
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name="اليوم",
    )
    start_time = models.TimeField(
        verbose_name="من",
    )
    end_time = models.TimeField(
        verbose_name="إلى",
    )
    note = models.CharField(
        max_length=200,
        verbose_name="ملاحظات",
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        day_name = dict(DAYS_OF_WEEK).get(self.day_of_week, self.day_of_week)
        return f"{self.teacher} - {day_name} {self.start_time}–{self.end_time}"


class TeacherMainSlot(BaseTeacherSlot):
    """حصة في الجدول العام للمعلم"""

    class Meta(BaseTeacherSlot.Meta):
        verbose_name = "حصة في الجدول العام"
        verbose_name_plural = "الجدول العام للمعلمين"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "day_of_week", "start_time", "end_time"],
                name="unique_main_slot_per_teacher_time",
            ),
        ]


class TeacherWaitingSlot(BaseTeacherSlot):
    """حصة انتظار للمعلم"""

    class Meta(BaseTeacherSlot.Meta):
        verbose_name = "حصة انتظار للمعلم"
        verbose_name_plural = "جدول حصص الانتظار للمعلمين"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "day_of_week", "start_time", "end_time"],
                name="unique_waiting_slot_per_teacher_time",
            ),
        ]


class TeacherActivitySlot(BaseTeacherSlot):
    """حصة نشاط للمعلم"""

    class Meta(BaseTeacherSlot.Meta):
        verbose_name = "حصة نشاط للمعلم"
        verbose_name_plural = "جدول حصص النشاط للمعلمين"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "day_of_week", "start_time", "end_time"],
                name="unique_activity_slot_per_teacher_time",
            ),
        ]
