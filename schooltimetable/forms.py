from django import forms
from .models import (
    TeacherMainSlot, TeacherWaitingSlot, TeacherActivitySlot,
    DaySchedule, Period, SpecialDay,
    Teacher, DAYS_OF_WEEK,
)


# ── نموذج مشترك لحصص المعلمين ──────────────────────────────────────────────

class _BaseSlotForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.order_by("name"),
        label="المعلم",
        empty_label="— اختر المعلم —",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    day_of_week = forms.ChoiceField(
        choices=[("", "— اختر اليوم —")] + list(DAYS_OF_WEEK),
        label="اليوم",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    start_time = forms.TimeField(
        label="وقت البداية",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-input"}),
    )
    end_time = forms.TimeField(
        label="وقت النهاية",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-input"}),
    )
    note = forms.CharField(
        label="ملاحظة",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "اختياري"}),
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("وقت النهاية يجب أن يكون بعد وقت البداية.")
        return cleaned


class TeacherMainSlotForm(_BaseSlotForm):
    class Meta:
        model = TeacherMainSlot
        fields = ["teacher", "day_of_week", "start_time", "end_time", "note"]


class TeacherWaitingSlotForm(_BaseSlotForm):
    class Meta:
        model = TeacherWaitingSlot
        fields = ["teacher", "day_of_week", "start_time", "end_time", "note"]


class TeacherActivitySlotForm(_BaseSlotForm):
    class Meta:
        model = TeacherActivitySlot
        fields = ["teacher", "day_of_week", "start_time", "end_time", "note"]


# ── إدارة الجداول اليومية ───────────────────────────────────────────────────

class DayScheduleForm(forms.ModelForm):
    day_of_week = forms.ChoiceField(
        choices=[("", "— اختر اليوم —")] + list(DAYS_OF_WEEK),
        label="اليوم",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    description = forms.CharField(
        label="وصف الجدول",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "مثال: جدول أسبوعي عادي"}),
    )
    is_active = forms.BooleanField(
        label="مفعّل",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )

    class Meta:
        model = DaySchedule
        fields = ["day_of_week", "description", "is_active"]


class PeriodForm(forms.ModelForm):
    name = forms.CharField(
        label="اسم الفترة",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "مثال: الحصة الأولى"}),
    )
    period_type = forms.ChoiceField(
        choices=Period.PERIOD_TYPES,
        label="نوع الفترة",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    order = forms.IntegerField(
        label="الترتيب",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
    )
    start_time = forms.TimeField(
        label="وقت البداية",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-input"}),
    )
    end_time = forms.TimeField(
        label="وقت النهاية",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-input"}),
    )
    subject = forms.CharField(
        label="المادة",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "اختياري"}),
    )
    teacher_name = forms.CharField(
        label="اسم المعلم",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "اختياري"}),
    )

    class Meta:
        model = Period
        fields = ["name", "period_type", "order", "start_time", "end_time", "subject", "teacher_name"]

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("وقت النهاية يجب أن يكون بعد وقت البداية.")
        return cleaned


# ── الأيام الخاصة ───────────────────────────────────────────────────────────

class SpecialDayForm(forms.ModelForm):
    date = forms.DateField(
        label="التاريخ",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-input"}),
    )
    schedule = forms.ModelChoiceField(
        queryset=DaySchedule.objects.filter(is_active=True).order_by("day_of_week"),
        label="الجدول الخاص",
        required=False,
        empty_label="— بدون جدول خاص —",
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    is_active = forms.BooleanField(
        label="مفعّل",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    note = forms.CharField(
        label="ملاحظة",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "مثال: يوم اختبار"}),
    )

    class Meta:
        model = SpecialDay
        fields = ["date", "schedule", "is_active", "note"]
