from django.conf import settings
from django.shortcuts import redirect

_PUBLIC_PREFIXES = (
    "/accounts/login/",
    "/accounts/logout/",
    "/accounts/register/",
    "/admin/",
    settings.STATIC_URL,
)


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/" or request.user.is_authenticated:
            return self.get_response(request)

        if any(request.path.startswith(p) for p in _PUBLIC_PREFIXES):
            return self.get_response(request)

        return redirect(f"/?next={request.path}")
