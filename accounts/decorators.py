from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')

        Profile.objects.get_or_create(user=user)

        if user.profile.is_doctor:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access restricted to doctors.")
        return redirect('profile')
    return _wrapped
