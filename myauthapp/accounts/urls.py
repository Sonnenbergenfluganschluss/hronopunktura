from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    home, index, 
    process_birthday, process_city, process_our_date, process_method, city_search,
    register, verify_email, profile, registration_sent, email_verified, 
    verification_expired, invalid_verification, get_luo_taiyan,
)

urlpatterns = [ 
     path('', views.home, name='home'),
     path('accounts/index', views.index, name='index'),
     path('process_birthday/', views.process_birthday, name='process_birthday'),
     path('city_search/', views.city_search, name='city_search'),
     path('process_city/', views.process_city, name='process_city'),
     path('process_our_date/', views.process_our_date, name='process_our_date'),
     path('process_method/', views.process_method, name='process_method'),
     path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('accounts/profile/', views.profile, name='profile'),
     path('city-search/', views.city_search, name='city_search'),
     path('accounts/password_reset/', 
          auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
          name='password_reset'),
     path('accounts/password_reset/done/', 
          auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
          name='password_reset_done'),
     path('accounts/reset/<uidb64>/<token>/', 
          auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
          name='password_reset_confirm'),
     path('accounts/reset/done/', 
          auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
          name='password_reset_complete'),
     path('register/', views.register, name='register'),
     path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
     path('registration-sent/', views.registration_sent, name='registration_sent'),
     path('email-verified/', views.email_verified, name='email_verified'),
     path('verification-expired/', views.verification_expired, name='verification_expired'),
     path('invalid-verification/', views.invalid_verification, name='invalid_verification'),
     path('get_luo_taiyan/', views.get_luo_taiyan, name='get_luo_taiyan'),
]