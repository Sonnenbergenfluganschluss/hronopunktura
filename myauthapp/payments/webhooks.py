from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from yookassa import Configuration, Webhook
from .models import Payment as PaymentModel, Subscription

@csrf_exempt
def yookassa_webhook(request):
    event_json = request.body
    # Проверяем подпись уведомления (защита от фальшивых запросов)
    try:
        event = Webhook.parse(event_json)
    except Exception as e:
        return HttpResponse(status=400)

    if event.event == 'payment.succeeded':
        payment = event.object
        # Обновляем статус платежа в БД
        PaymentModel.objects.filter(transaction_id=payment.id).update(status='success')
        # Активируем подписку
        subscription = Subscription.objects.get(id=payment.metadata['subscription_id'])
        subscription.is_active = True
        subscription.save()

    return HttpResponse(status=200)