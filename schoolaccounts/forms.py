# schoolaccounts/forms.py

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    """
    فورم تسجيل مستخدم جديد بالاعتماد على نموذج المستخدم الافتراضي.
    يمكن استخدامه لاحقًا في صفحة /accounts/register/ مثلاً.
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
        help_text="سيُستخدم البريد الإلكتروني في استعادة كلمة المرور.",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )
        labels = {
            "username": "اسم المستخدم",
            "password1": "كلمة المرور",
            "password2": "تأكيد كلمة المرور",
        }
        help_texts = {
            "username": "",
        }

    def clean_email(self):
        """
        التحقق من أن البريد الإلكتروني غير مستخدم مسبقًا
        لتقليل الأخطاء ومشاكل استعادة كلمة المرور.
        """
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل.")
        return email

    def __init__(self, *args, **kwargs):
        """
        ضبط بعض خصائص الحقول (مثل placeholder / autocomplete) بطريقة
        تساعد في تجربة المستخدم دون المساس بالأمان.
        """
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "اسم المستخدم"
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "اختر اسم مستخدم",
                "autocomplete": "username",
            }
        )

        # إخفاء نصوص المساعدة الإنجليزية الافتراضية
        for name in ["password1", "password2"]:
            self.fields[name].help_text = ""
            self.fields[name].widget.attrs.update(
                {
                    "autocomplete": "new-password",
                }
            )


class UserLoginForm(AuthenticationForm):
    """
    نموذج تسجيل الدخول، مع تخصيص بسيط للواجهات فقط.
    """

    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(
            attrs={
                "placeholder": "اسم المستخدم",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="كلمة المرور",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "كلمة المرور",
                "autocomplete": "current-password",
            }
        ),
    )

    def confirm_login_allowed(self, user):
        """
        نقطة توسيع مستقبلية:
        - منع دخول مستخدمين موقوفين
        - التحقق من تفعيل البريد، إلخ.
        حاليًا نترك السلوك الافتراضي لـ Django.
        """
        super().confirm_login_allowed(user)


class SchoolPasswordResetForm(PasswordResetForm):
    """
    نموذج طلب إعادة تعيين كلمة المرور.
    يمكن لاحقًا تخصيص رسالة البريد أو طريقة الإرسال.
    """

    email = forms.EmailField(
        label="البريد الإلكتروني",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "أدخل بريدك المسجّل في النظام",
                "autocomplete": "email",
            }
        ),
    )


class SchoolSetPasswordForm(SetPasswordForm):
    """
    نموذج تعيين كلمة مرور جديدة بعد الضغط على رابط الاستعادة.
    """

    new_password1 = forms.CharField(
        label="كلمة المرور الجديدة",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "أدخل كلمة مرور قوية",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="تأكيد كلمة المرور الجديدة",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "أعد إدخال كلمة المرور",
            }
        ),
    )
