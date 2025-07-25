from django.utils import timezone
from .models import Subscription

def subscription_status(request):
    if request.user.is_authenticated:
        active_subscription = Subscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gte=timezone.now()
        ).first()
        return {'has_active_subscription': bool(active_subscription)}
    return {'has_active_subscription': False}