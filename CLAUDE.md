# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Run dev server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Generate migrations after model changes
python manage.py makemigrations <app_name> --name <description>

# Create superuser
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic
```

## Architecture

Django 5.0 school timetable system for مدرسة الخالدية الابتدائية. Arabic RTL UI (`LANGUAGE_CODE = "ar"`, `TIME_ZONE = "Asia/Riyadh"`). SQLite in development; configured for S3/Azure via `STORAGE_BACKEND` env var in production.

### App structure

| App | Responsibility |
|---|---|
| `schoolcore` | `SchoolConfig` singleton (school name, timezone, logo) |
| `schoolaccounts` | `UserProfile` extending Django's User with role-based access |
| `schooltimetable` | All scheduling models + admin |
| `schooldisplay` | All views and templates — dashboard, control panel, boards |

All business logic views live in `schooldisplay/views.py`. The `schooltimetable` app owns models and forms; `schooldisplay` imports from it.

### URL routing

- `/` — login page (home view)
- `/dashboard/` — main timetable dashboard
- `/timetable/` — `schooltimetable.urls` namespace (API views)
- `/admin/` — Django admin

### Role system

Four roles in `UserProfile.ROLES`: `admin`, `supervisor`, `teacher`, `display`. The `_require_role()` decorator in `schooldisplay/views.py` guards views. Superusers always get `admin` role. A `post_save` signal in `schoolaccounts/models.py` auto-creates a `UserProfile` for every new User with role `display`.

`LoginRequiredMiddleware` (`khalidiyaschool/middleware.py`) redirects unauthenticated users to `/`. Login is by **email** (not username) via `khalidiyaschool/auth_backends.EmailBackend`.

### Scheduling data model

- `DaySchedule` — a named schedule for a given day of week (Sun=0 … Thu=4, Saudi week)
- `Period` — a time slot within a `DaySchedule` (class/break/activity/other), with optional subject and teacher name
- `SpecialDay` — date-specific schedule override; takes priority over the regular weekday schedule
- `DailyTimeSlot` — canonical bell times per day/period number (separate from `Period`)
- `Teacher` + `TeacherMainSlot` / `TeacherWaitingSlot` / `TeacherActivitySlot` — teacher registry and their time assignments

`schooltimetable/services.py` provides `get_today_schedule()` and `get_periods_with_state()` — use these in views rather than reimplementing the SpecialDay → weekday fallback logic.

### Image pipeline

Every `ImageField` in the project auto-converts uploads to WebP via `khalidiyaschool/utils/images.py`. The conversion runs in each model's `save()` — not in forms — so it applies regardless of how data arrives. Models with images: `Teacher.photo`, `SchoolConfig.logo`, `UserProfile.avatar`.

`SchoolConfig.save()` also deletes the old logo file when replaced (singleton pattern).

### Environment variables (`.env`)

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Required in production; dev falls back to a hard-coded unsafe key when `DEBUG=True` |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Comma-separated list |
| `TIME_ZONE` | Defaults to `Asia/Riyadh` |
| `STORAGE_BACKEND` | `s3`, `azure`, or empty (local `media/` directory) |
| `AWS_*` / `AZURE_*` | Cloud storage credentials — only read when `STORAGE_BACKEND` matches |

Media files are served by Django only when `DEBUG=True` (see `urls.py`). In production, cloud storage serves files directly.
