from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from payments.models import Tariff
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from .forms import RegisterForm, CustomUserChangeForm
from .models import CustomUser



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # save() уже установит is_active=False и сгенерирует токен
            
            # Отправляем email для верификации
            subject = 'Подтверждение email'
            html_message = render_to_string('registration/verification_email.html', {
                'user': user,
                'verification_link': f"http://{request.get_host()}/verify-email/{user.verification_token}/",
            })
            
            email = EmailMessage(
                subject,
                html_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.content_subtype = "html"
            email.send()
            
            return redirect('registration_sent')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, token):
    try:
        # Ищем пользователя по токену верификации
        user = CustomUser.objects.get(verification_token=token)
        
        if user.is_verification_token_expired():
            # Генерируем новый токен и отправляем письмо повторно
            user.generate_verification_token()
            
            # Отправляем новое письмо
            subject = 'Новая ссылка для подтверждения email'
            html_message = render_to_string('registration/verification_email.html', {
                'user': user,
                'verification_link': f"http://{request.get_host()}/verify-email/{user.verification_token}/",
            })
            
            email = EmailMessage(
                subject,
                html_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.content_subtype = "html"
            email.send()
            
            return redirect('verification_expired')
            
        # Подтверждаем email используя метод модели
        if user.verify_email(token):
            return redirect('email_verified')
        else:
            return redirect('invalid_verification')
            
    except CustomUser.DoesNotExist:
        return redirect('invalid_verification')

# Простые view для страниц статуса
def registration_sent(request):
    return render(request, 'registration/registration_sent.html')

def email_verified(request):
    return render(request, 'registration/email_verified.html')

def verification_expired(request):
    return render(request, 'registration/verification_expired.html')

def invalid_verification(request):
    return render(request, 'registration/invalid_verification.html')

@login_required
def profile(request):
    active_tariff = Tariff.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль обновлен!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'active_tariff': active_tariff,
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)
