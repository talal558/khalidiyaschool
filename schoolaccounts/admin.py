# schoolaccounts/admin.py

from django.contrib import admin

"""
ملف لوحة التحكم لتطبيق schoolaccounts

حاليًا نستخدم نموذج المستخدم الافتراضي لـ Django، لذلك لا نحتاج
لتسجيل موديلات إضافية هنا في الوقت الحالي.

عند إضافة موديلات مثل:
- Teacher
- Student
- Parent
يمكن تسجيلها هنا باستخدام admin.site.register(...)
مثال:

from .models import Teacher, Student, Parent

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "specialization")
    search_fields = ("user__username", "user__first_name", "user__last_name")

"""

# لا يوجد تسجيل لموديلات إضافية حاليًا.
# Django يقوم تلقائيًا بتسجيل نموذج User عبر django.contrib.auth.admin.
