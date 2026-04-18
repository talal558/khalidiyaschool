from urllib.parse import quote

from django.conf import settings
from django.shortcuts import redirect

_PUBLIC_PREFIXES = (
    "/accounts/login/",
    "/accounts/logout/",
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

        # URL-encode the path to prevent header injection
        safe_next = quote(request.path, safe="/?=&")
        return redirect(f"/?next={safe_next}")
