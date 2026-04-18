_ROLE_LABELS = {
    'admin':      'مدير',
    'supervisor': 'مشرف',
    'teacher':    'معلم',
    'display':    'عرض فقط',
}


def user_role_context(request):
    if not request.user.is_authenticated:
        return {'user_role': None, 'user_role_display': ''}
    if request.user.is_superuser:
        role = 'admin'
    else:
        try:
            role = request.user.profile.role
        except Exception:
            role = 'display'
    return {
        'user_role': role,
        'user_role_display': _ROLE_LABELS.get(role, ''),
    }
