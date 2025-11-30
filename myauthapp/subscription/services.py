# subscription/services.py
from django.core.mail import send_mail
from django.conf import settings

def send_subscription_request_email(user, tariff, request=None):
    domain = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'

    """
    Отправляет email администратору с запросом на подписку
    """
    subject = f'Запрос на оформление подписки "{tariff.name}" от {user.username}'
    
    message = f"""
    Поступил новый запрос на оформление подписки:
    
    Пользователь: {user.username}
    Email: {user.email}
    Тариф: {tariff.name}
    Цена: {tariff.price} ₽
    Продолжительность: {tariff.duration_days} дней
    Описание: {tariff.description}
    
    Для активации подписки перейдите в административную панель:
    {protocol}://{domain}/admin/payments/subscription/
    
    Пользователь ожидает подтверждения подписки.
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False