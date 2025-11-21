from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("schooldisplay:dashboard")  # بعد تسجيل الدخول
        else:
            return render(request, "schoolaccounts/login.html", {
                "error": "اسم المستخدم أو كلمة المرور غير صحيحة"
            })

    return render(request, "schoolaccounts/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # التحقق من كلمات المرور
        if password1 != password2:
            return render(request, "schoolaccounts/register.html", {
                "error": "كلمتا المرور غير متطابقتين"
            })

        # التأكد أن المستخدم غير موجود
        if User.objects.filter(username=username).exists():
            return render(request, "schoolaccounts/register.html", {
                "error": "اسم المستخدم مستخدم مسبقًا"
            })

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        login(request, user)  # تسجيل دخوله مباشرة
        return redirect("schooldisplay:dashboard")

    return render(request, "schoolaccounts/register.html")
