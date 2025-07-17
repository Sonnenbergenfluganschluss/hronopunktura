# from django.urls import path
# from . import views
# from django.views.decorators.csrf import csrf_exempt
# from . import webhooks


from django.urls import path
from . import views


app_name = 'payments'  # Это определяет namespace

urlpatterns = [
    path('create/<int:tariff_id>/', views.create_payment, name='create_payment'),
    path('tariffs/', views.tariff_list, name='tariff_list'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('webhook/', views.yookassa_webhook, name='yookassa_webhook'),
]