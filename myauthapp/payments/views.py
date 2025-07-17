from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from yookassa import Configuration, Payment
from .models import Tariff, Subscription, Payment as PaymentModel
import uuid
from datetime import datetime

Configuration.configure(
    settings.YOOKASSA_SHOP_ID,
    settings.YOOKASSA_SECRET_KEY
)

@login_required
def create_payment(request, tariff_id):
    try:
        tariff = Tariff.objects.get(id=tariff_id)
        
        # Создаем платеж в ЮKassa
        payment = Payment.create(
            {
            "status": "pending",
            "paid": False,
            "amount": {
                "value": str(tariff.price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
            "return_url": request.build_absolute_uri(reverse('payments:payment_success'))        
            },
            "created_at": datetime.now(),
            "description": f"Оплата тарифа {tariff.name}",
            "metadata": {
                "user_id": request.user.id,
                "tariff_id": tariff.id
            },
            "refundable": False,
            "test": True,
            }, str(uuid.uuid4()))
        
        # Сохраняем платеж в БД
        PaymentModel.objects.create(
            user=request.user,
            amount=tariff.price,
            payment_id=payment.id,
            status=payment.status,
            tariff=tariff
        )
        
        return redirect(payment.confirmation.confirmation_url)

    except Tariff.DoesNotExist:
        return payment_failed(request, "Выбранный тариф не существует")
    except Exception as e:
        # logger.error(f"Payment error: {str(e)}")
        return payment_failed(request, str(e), tariff_id)


@login_required
def tariff_list(request):
    tariffs = Tariff.objects.filter(is_active=True)
    return render(request, 'payments/tariffs.html', {'tariffs': tariffs})


@login_required
def payment_cancel(request):
    return render(request, 'payments/cancel.html')

def yookassa_webhook(request):
    # Обработка вебхука от ЮKassa
    # Важно: реализовать проверку подписи запроса!
    pass

@login_required
def payment_success(request):
    # Проверяем статус платежа (можно через Webhook или вручную)
    payment_id = request.GET.get('payment_id')
    if payment_id:
        payment = Payment.find_one(payment_id)
        if payment.status == 'succeeded':
            # Активируем подписку
            subscription = Subscription.objects.get(id=payment.metadata['subscription_id'])
            subscription.is_active = True
            subscription.save()

            # Обновляем статус платежа
            PaymentModel.objects.filter(transaction_id=payment_id).update(status='success')

            return render(request, 'payments/success.html', {
                'tariff': subscription.tariff,
                'end_date': subscription.end_date
            })
    
    return redirect(reverse('payments:payment_failed'))

@login_required
def payment_failed(request, error=None, tariff_id=None):
    return render(request, 'payments/failed.html', {
        'error': error,
        'tariff_id': tariff_id
    })



@login_required
def pricing(request):
    tariffs = Tariff.objects.all()  # Получаем все тарифы из БД
    return render(request, 'payments/pricing.html', {'tariffs': tariffs})