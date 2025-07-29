from asyncio.log import logger
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotification

from payments.utils import cache_subscription_status
from .models import Tariff, Subscription, Payment as PaymentModel
import uuid


# Настройка логгера
logger = logging.getLogger(__name__)

# Конфигурация ЮKassa
Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)

@login_required
def create_payment(request, tariff_id):
    try:
        tariff = Tariff.objects.get(id=tariff_id)
        
        # Создаем подписку (неактивную до оплаты)
        subscription = Subscription.objects.create(
            user=request.user,
            tariff=tariff,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=tariff.duration_days),
            is_active=False
        )

        # Генерируем уникальный ID для платежа
        payment_uuid = str(uuid.uuid4())

        # Корректные данные для ЮKassa
        payment_data = {
            "amount": {
                "value": str(tariff.price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(
                    reverse('payments:payment_success') + f"?payment_id={payment_uuid}"
                )
            },
            "description": f"Оплата тарифа {tariff.name}",
            "metadata": {
                "user_id": request.user.id,
                "tariff_id": tariff.id,
                "subscription_id": subscription.id,
                "payment_id": payment_uuid
            },
            "capture": True  # Автоматическое подтверждение платежа
        }
        print('payment_data: ', payment_data)
        # Создаем платеж в ЮKassa
        yookassa_payment = Payment.create(payment_data)

        print('payment.id: ', payment_uuid)
        print('yookassa_payment.id: ', yookassa_payment.id)
        # Сохраняем платеж в БД
        PaymentModel.objects.create(
            user=request.user,
            amount=tariff.price,
            payment_id=payment_uuid,
            yookassa_payment_id=yookassa_payment.id,
            status='pending',
            tariff=tariff,
            subscription=subscription
        )

        return redirect(yookassa_payment.confirmation.confirmation_url)

    except Tariff.DoesNotExist:
        return payment_failed(request, "Тариф не найден")
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {str(e)}", exc_info=True)
        return payment_failed(request, "Ошибка при создании платежа")


@login_required
def tariff_list(request):
    tariffs = Tariff.objects.filter(is_active=True)
    return render(request, 'payments/tariffs.html', {'tariffs': tariffs})


@login_required
def payment_cancel(request):
    return render(request, 'payments/cancel.html')

@csrf_exempt
def yookassa_webhook(request):

    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed")

    try:
        notification = WebhookNotification(request.body)
        if not notification.validate(settings.YOOKASSA_WEBHOOK_SECRET):
            print("Invalid signature")
            return HttpResponseBadRequest("Invalid signature")
        
        event_data = json.loads(request.body)
        payment_id = event_data['object']['id']
        
        # Получаем данные платежа из ЮKassa
        yookassa_payment = Payment.find_one(payment.yookassa_payment_id)
        
        # Обрабатываем только успешные платежи
        if yookassa_payment.status == 'succeeded':
            metadata = yookassa_payment.metadata
            payment_id = metadata.get('payment_id')
            
            if not payment_id:
                logger.error("No payment_id in metadata")
                return HttpResponseBadRequest("Invalid metadata")

            # Находим платеж в нашей БД
            payment = PaymentModel.objects.get(
                payment_id=payment_id,
                status__in=['pending', 'succeeded']  # Защита от повторной обработки
            )
            
            # Обновляем статус
            payment.status = 'succeeded'
            payment.yookassa_payment_id = payment_id
            payment.save()

            # Активируем подписку
            subscription = payment.subscription
            subscription.is_active = True
            subscription.save()

            logger.info(f"Подписка {subscription.id} активирована для пользователя {payment.user.id}")

        return HttpResponse("OK", status=200)

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return HttpResponseBadRequest("Error")



@login_required
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    
    if not payment_id:
        return payment_failed(request, "Не указан ID платежа")

    try:
        # Ищем платеж в БД
        payment = PaymentModel.objects.get(payment_id=payment_id, user=request.user)
        
        # Если вебхук уже обработал платеж, показываем успех
        if payment.status == 'succeeded':
            return render(request, 'payments/success.html', {
                'tariff': payment.tariff,
                'end_date': payment.subscription.end_date
            })
        else:
            # Если статус не обновлён, проверяем через API ЮKassa
            print('yookassa_payment: ', payment.yookassa_payment_id)
            yookassa_payment = Payment.find_one(payment.yookassa_payment_id)
            print(yookassa_payment.id)
            print(yookassa_payment.status)
            print(yookassa_payment.id)
             
            if yookassa_payment.status == 'succeeded':
                # Обновляем статус вручную (на случай, если вебхук ещё не пришёл)
                payment.status = 'succeeded'
                payment.save()
                
                # Активируем подписку
                subscription = payment.subscription
                subscription.is_active = True
                subscription.save()
                
                return render(request, 'payments/success.html', {
                    'payment': payment,
                    'end_date': payment.subscription.end_date
                })

            return payment_failed(request, "Платеж не завершён")

    except PaymentModel.DoesNotExist:
        return payment_failed(request, "Платеж не найден в базе данных")
    except Exception as e:
        logger.error(f"Payment success error: {str(e)}")
        return payment_failed(request, f"Ошибка: {str(e)}")

@login_required
def payment_failed(request, error=None, tariff_id=None):
    return render(request, 'payments/failed.html', {
        'error': error,
        'tariff_id': tariff_id
    })



# Проверка подписки и кэша для доступа к контенту
@cache_subscription_status()
def check_subscription(user):
    return Subscription.objects.filter(
        user=user,
        is_active=True,
        end_date__gte=timezone.now()
    ).exists()

