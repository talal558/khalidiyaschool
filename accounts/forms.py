# accounts/forms.py

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """
    نموذج تسجيل مستخدم جديد (المستخدم الافتراضي)
    """

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="الاسم الأول",
        widget=forms.TextInput(
            attrs={
                "placeholder": "أدخل الاسم الأول",
                "autocomplete": "given-name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="اسم العائلة",
        widget=forms.TextInput(
            attrs={
                "placeholder": "أدخل اسم العائلة",
                "autocomplete": "family-name",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        label="البريد الإلكتروني",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "example@school.com",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
        labels = {
            "username": "اسم المستخدم",
            "password1": "كلمة المرور",
            "password2": "تأكيد كلمة المرور",
        }

    def clean_email(self):
        """
        التأكد من عدم تكرار البريد الإلكتروني
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("البريد الإلكتروني مستخدم مسبقًا.")
        return email


class LoginForm(AuthenticationForm):
    """
    نموذج تسجيل الدخول الافتراضي
    """

    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={"placeholder": "اسم المستخدم"}),
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"placeholder": "كلمة المرور"}),
    )


class ResetPasswordForm(PasswordResetForm):
    """
    نموذج إرسال رابط استعادة كلمة المرور
    """

    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={"placeholder": "أدخل بريدك"}),
    )


class SetNewPasswordForm(SetPasswordForm):
    """
    نموذج إدخال كلمة المرور الجديدة
    """

    new_password1 = forms.CharField(
        label="كلمة المرور الجديدة",
        widget=forms.PasswordInput(attrs={"placeholder": "كلمة مرور قوية"}),
    )
    new_password2 = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={"placeholder": "أعد إدخال كلمة المرور"}),
    )
