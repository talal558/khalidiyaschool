from django.shortcuts import render

def dashboard(request):
    return render(request, "display/dashboard.html", {
        "page_title": "لوحة التوقيت المدرسي",
        "app_name": "khalidiyaschool",
    })
