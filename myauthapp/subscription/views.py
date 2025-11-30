# subscription/views.py

from datetime import timedelta, datetime
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from payments.models import Tariff, Subscription
from .services import send_subscription_request_email
# from .models import SubscriptionRequest

@login_required
def request_subscription(request, tariff_id):
    """
    Обрабатывает запрос на подписку
    """
    user = request.user
    tariff = get_object_or_404(Tariff, id=tariff_id)
    
    # Проверяем, не отправлял ли пользователь уже запрос на этот тариф
    existing_request = Subscription.objects.filter(
        user=user, 
        is_active=True        
    ).first()
    
    if existing_request:
        messages.warning(request, 'У вас уже есть активный запрос на подписку')
        return HttpResponseRedirect('/')
        # return redirect('payments:tariff_list')  # или на страницу тарифов
    
    
    # Проверяем, нет ли уже pending-подписки
    pending_subscription = Subscription.objects.filter(
        user=user,
        is_active=False,
        start_date__isnull=True
    ).first()
    
    if pending_subscription:
        messages.warning(request, 'У вас уже есть запрос на подписку, ожидающий подтверждения')
        return HttpResponseRedirect('/')
    
    # Рассчитываем даты подписки
    start_date = datetime.now()
    end_date = start_date + timedelta(days=tariff.duration_days)


    # Отправляем email администратору
    email_sent = send_subscription_request_email(user, tariff, request)
    
    # Сохраняем запрос в базе данных
    subscription = Subscription.objects.create(
        user=user,
        tariff=tariff,
        start_date=start_date,  # Будет установлена администратором при активации
        end_date=end_date,    # Будет установлена администратором при активации
        is_active=False   # Не активна до подтверждения администратором
    )
    
    if email_sent:
        messages.success(request, f'Запрос на подписку "{tariff.name}" отправлен администратору!')
        return redirect('subscription:subscription_success')
    else:
        messages.error(request, 'Произошла ошибка при отправке запроса')
        return redirect('payments:tariffs')

def subscription_success(request):
    """
    Страница успешной отправки запроса
    """
    return render(request, 'subscription/success.html')