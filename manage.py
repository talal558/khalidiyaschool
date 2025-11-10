#!/usr/bin/env python
import os
import sys

def main():
    """نقطة تشغيل مشروع Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "khalidiyaschool.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "تعذر استيراد Django. تأكد من تثبيته في البيئة الافتراضية."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
