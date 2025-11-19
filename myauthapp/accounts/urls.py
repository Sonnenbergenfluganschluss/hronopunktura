from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import (
    register, verify_email, profile, registration_sent, email_verified, 
    verification_expired, invalid_verification,
)

urlpatterns = [ 

     path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('accounts/profile/', views.profile, name='profile'),
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
]