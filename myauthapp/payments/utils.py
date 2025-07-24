# Декоратор для кеширования

from django.core.cache import cache
from functools import wraps

def cache_subscription_status(timeout=3600):  # 1 час
    def decorator(func):
        @wraps(func)
        def wrapper(user):
            cache_key = f"user_{user.id}_subscription_status"
            status = cache.get(cache_key)
            if status is None:
                status = func(user)
                cache.set(cache_key, status, timeout)
            return status
        return wrapper
    return decorator