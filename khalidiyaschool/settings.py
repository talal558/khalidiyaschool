import os
from pathlib import Path
from dotenv import load_dotenv

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# تحميل ملف .env من جذر المشروع
load_dotenv(BASE_DIR / ".env")

# مفاتيح الأمان — يجب تعيين SECRET_KEY في ملف .env قبل النشر
_secret = os.getenv("SECRET_KEY", "")
if not _secret:
    if os.getenv("DEBUG", "False").lower() == "true":
        _secret = "dev-only-unsafe-key-never-use-in-production-abc123xyz"
    else:
        raise RuntimeError(
            "SECRET_KEY غير محدد في ملف .env — أضفه قبل تشغيل الخادم."
        )
SECRET_KEY = _secret

# وضع التطوير أو الإنتاج
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# الهوستات المسموح لها
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

# التطبيقات المثبتة
INSTALLED_APPS = [
    # تطبيقات Django الأساسية
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # مكتبة تحسين قوالب الفورم (مطلوبة لحل add_class)
    "widget_tweaks",

    # تطبيقات المشروع
    "schoolcore",
    "schoolaccounts",
    "schooltimetable",
    "schooldisplay",
]

# الوسائط (Middleware)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "khalidiyaschool.middleware.LoginRequiredMiddleware",
]

# ملف الروابط الرئيسي
ROOT_URLCONF = "khalidiyaschool.urls"

# إعدادات القوالب (Templates)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # مجلد عام للقوالب في جذر المشروع: khalidiyaschool/templates/
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "schoolaccounts.context_processors.user_role_context",
            ],
        },
    },
]

# تطبيق WSGI
WSGI_APPLICATION = "khalidiyaschool.wsgi.application"

# قاعدة البيانات الافتراضية (SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# التحقق من قوة كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# اللغة والمنطقة الزمنية
LANGUAGE_CODE = "ar"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Riyadh")
USE_I18N = True
USE_TZ = True

# الملفات الثابتة
STATIC_URL = "/static/"

# مجلدات الملفات الثابتة في وضع التطوير
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]

# في وضع الإنتاج يمكن تفعيل STATIC_ROOT ليتم جمع الملفات فيه
# STATIC_ROOT = BASE_DIR / "static"

# الإعداد الافتراضي لمفتاح الحقول
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# إعدادات تسجيل الدخول
LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# خلفيات المصادقة — تدعم تسجيل الدخول بالبريد الإلكتروني
AUTHENTICATION_BACKENDS = [
    "khalidiyaschool.auth_backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ── إعدادات الأمان ──────────────────────────────────────────────────────────

# منع تخمين نوع المحتوى (MIME sniffing)
SECURE_CONTENT_TYPE_NOSNIFF = True

# حماية ضد تضمين الصفحة في iframe خارجي
X_FRAME_OPTIONS = "DENY"

# الكوكيز — httpOnly يمنع قراءتها من JavaScript
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# مدة الجلسة: 8 ساعات (يوم دراسي + هامش)
SESSION_COOKIE_AGE = 28800

# إنهاء الجلسة عند إغلاق المتصفح
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# إعدادات الإنتاج — فعّلها في .env عند النشر على HTTPS
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
