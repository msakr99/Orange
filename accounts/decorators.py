from django.shortcuts import redirect
from functools import wraps

def allowed_user_types(allowed_types=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.user_type not in allowed_types:
                return redirect('unauthorized')  # صفحة ترفض الدخول
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



# decorators.py

from django.http import HttpResponseForbidden

def pharmacy_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'pharmacy':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("ليس لديك صلاحية للوصول إلى هذه الصفحة.")
    return wrapper
