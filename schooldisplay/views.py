from django.shortcuts import render


def display_dashboard(request):
    """
    شاشة العرض الرئيسية (home) التي تظهر فيها الساعة + جدول اليوم + جداول المعلمين.
    """
    return render(request, "home.html")


def control_panel(request):
    """
    صفحة لوحة التحكم (جدول المعلمين):
    - تعرض ساعة بسيطة
    - وجدول حصص المعلمين من الجدول العام (TeacherMainSlot).
    """
    return render(request, "teacher_control.html")
