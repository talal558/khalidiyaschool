# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

"""
لوحة التحكم لتطبيق accounts
بما أننا نستخدم نموذج المستخدم الافتراضي،
فلا نحتاج إلى تخصيص كبير هنا، لكن يمكن لاحقًا
تعديل UserAdmin لإضافة حقول مثل (role) وغير ذلك.
"""

# تسجيل نموذج المستخدم الافتراضي
admin.site.unregister(User)  # إلغاء التسجيل القديم
admin.site.register(User, UserAdmin)  # تسجيله مع واجهته الأساسية
