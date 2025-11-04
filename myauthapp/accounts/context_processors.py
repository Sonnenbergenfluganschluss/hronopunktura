# accounts/context_processors.py
from django.conf import settings

def email_settings(request):
    return {
        'email_settings': {
            'EMAIL_HOST': settings.EMAIL_HOST,
            'EMAIL_PORT': settings.EMAIL_PORT,
            'EMAIL_USE_SSL': settings.EMAIL_USE_SSL,
            'EMAIL_USE_TLS': settings.EMAIL_USE_TLS,
            'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
            'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
        }
    }