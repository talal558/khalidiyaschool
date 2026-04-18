from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class UserProfile(models.Model):
    ROLES = [
        ('admin',      'مدير'),
        ('supervisor', 'مشرف'),
        ('teacher',    'معلم'),
        ('display',    'عرض فقط'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField('الصلاحية', max_length=20, choices=ROLES, default='display')

    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def can_manage(self):
        return self.role in ('admin', 'supervisor')

    @property
    def is_admin_role(self):
        return self.role == 'admin'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
