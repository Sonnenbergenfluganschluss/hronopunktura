from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from .models import Subscription

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            reverse('payments:tariff_list'),
            reverse('payments:create_payment'),
            # Добавьте другие URL, которые должны быть доступны без подписки
        ]

    def __call__(self, request):
        response = self.get_response(request)
        
        if (request.user.is_authenticated and 
            not request.path_info in self.exempt_urls and
            not request.path_info.startswith('/admin/')):
            
            has_active_subscription = Subscription.objects.filter(
                user=request.user,
                is_active=True,
                end_date__gte=timezone.now()
            ).exists()
            
            if not has_active_subscription and not getattr(request, 'allow_without_subscription', False):
                # Перенаправляем на страницу с предложением подписки
                return redirect('payments:tariff_list')
        
        return response
    