from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label=_("Ваше имя"),
        max_length=150,
        error_messages={
            'required': _('Пожалуйста, введите имя пользователя'),
            'max_length': _('Имя пользователя не должно превышать 150 символов'),
            'invalid': _('Имя пользователя содержит недопустимые символы')
        }
    )
    
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': _('Пожалуйста, введите email'),
            'invalid': _('Введите корректный email адрес')
        }
    )
    
    password1 = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        error_messages={
            'required': _('Пожалуйста, введите пароль'),
        }
    )
    
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        error_messages={
            'required': _('Пожалуйста, подтвердите пароль'),
        }
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем все help_text
        for field_name in self.fields:
            self.fields[field_name].help_text = None
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # Пользователь неактивен до верификации email
        user.email_verified = False
        
        if commit:
            user.save()
            # Генерируем токен верификации после сохранения пользователя
            user.generate_verification_token()
            
        return user
      
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Имя пользователя"),
        error_messages={
            'required': _('Пожалуйста, введите имя пользователя'),
            'invalid': _('Неверное имя пользователя или пароль')
        }
    )
    
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': _('Пожалуйста, введите пароль'),
        }
    )
    
    error_messages = {
        'invalid_login': _(
            "Неверное имя пользователя или пароль. Обратите внимание, что оба поля "
            "могут быть чувствительны к регистру."
        ),
        'inactive': _("Этот аккаунт неактивен. Подтвердите ваш email для активации."),
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        
    def confirm_login_allowed(self, user):
        """
        Проверяем, может ли пользователь войти в систему.
        Переопределяем для кастомных сообщений об ошибках.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        super().confirm_login_allowed(user)

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Удаляем help_text для username
        self.fields['username'].help_text = None

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'birth_date', 'city')   #, 'profile_picture'
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Проверяем, что email не используется другим пользователем
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот email уже используется другим пользователем')
        return email