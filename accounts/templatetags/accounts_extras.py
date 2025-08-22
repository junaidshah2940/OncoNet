from django import template

register = template.Library()

@register.filter
def is_doctor(user):
    try:
        return hasattr(user, "profile") and bool(user.profile.is_doctor)
    except Exception:
        return False
