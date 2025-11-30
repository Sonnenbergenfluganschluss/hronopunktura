# subscription/urls.py
from django.urls import path
from . import views

app_name = 'subscription'

urlpatterns = [
    path('request/<int:tariff_id>/', views.request_subscription, name='request_subscription'),
    path('success/', views.subscription_success, name='subscription_success'),
]