from django.http import HttpResponseRedirect
from django.urls import reverse
from functools import wraps

def email_verified_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        
        if not request.user.email_verified:
            messages.warning(request, 'Для доступа к этой странице подтвердите ваш email')
            return HttpResponseRedirect(reverse('send_verification'))
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view