import os
from pathlib import Path
from dotenv import load_dotenv

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# تحميل ملف .env من جذر المشروع
load_dotenv(BASE_DIR / ".env")

# مفاتيح الأمان
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

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
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # تطبيقاتك أنت
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
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# اللغة والمنطقة الزمنية
LANGUAGE_CODE = "ar"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Riyadh")
USE_I18N = True
USE_TZ = True

# الملفات الثابتة
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# إعدادات تسجيل الدخول
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# حالياً نستخدم نموذج المستخدم الافتراضي لدجانغو
# (لا تضف AUTH_USER_MODEL هنا حتى نجهز موديل مخصص لاحقاً)
