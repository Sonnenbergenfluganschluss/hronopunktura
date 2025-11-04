# Инвалидация кеша

from django.core.cache import Cache
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Subscription

@receiver(post_save, sender=Subscription)
def clear_subscription_cache(sender, instance, **kwargs):
    Cache.delete(f"user_{instance.user.id}_subscription_status")


@receiver(pre_save, sender=Subscription)
def notify_on_subscription_end(sender, instance, **kwargs):
    if instance.pk:  # Только для существующих подписок
        old = Subscription.objects.get(pk=instance.pk)
        if old.is_active and not instance.is_active:
            send_mail(
                "Подписка завершена",
                f"Ваша подписка {instance.tariff.name} закончилась.",
                "noreply@example.com",
                [instance.user.email]
            )