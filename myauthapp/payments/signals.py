# Инвалидация кеша

from django.core.cache import Cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Subscription

@receiver(post_save, sender=Subscription)
def clear_subscription_cache(sender, instance, **kwargs):
    Cache.delete(f"user_{instance.user.id}_subscription_status")