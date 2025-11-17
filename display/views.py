from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def dashboard(request: HttpRequest) -> HttpResponse:
    """
    الصفحة الرئيسية للوحة التوقيت المدرسي.
    """
    context = {
        "page_title": "لوحة التوقيت المدرسي",
        "app_name": "khalidiyaschool",
    }
    return render(request, "display/dashboard.html", context)


def school_year_board(request: HttpRequest) -> HttpResponse:
    """
    صفحة لوحة العام المدرسي.
    """
    context = {
        "page_title": "لوحة العام المدرسي",
        "app_name": "khalidiyaschool",
    }
    return render(request, "display/school_year_board.html", context)


def control_panel(request: HttpRequest) -> HttpResponse:
    """
    لوحة التحكم (قابلة للتطوير لاحقًا).
    """
    context = {
        "page_title": "لوحة التحكم",
        "app_name": "khalidiyaschool",
    }
    return render(request, "display/control_panel.html", context)
