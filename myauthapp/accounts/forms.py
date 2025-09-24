from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        error_messages={
            'required': _('Пожалуйста, введите имя пользователя'),
            'max_length': _('Имя пользователя не должно превышать 150 символов'),
            'invalid': _('Имя пользователя содержит недопустимые символы')
        }
    )
    
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': _('Пожалуйста, введите пароль'),
        }
    )
    
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        error_messages={
            'required': _('Пожалуйста, подтвердите пароль'),
        }
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем все help_text
        for field_name in self.fields:
            self.fields[field_name].help_text = None

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        error_messages={
            'required': _('Пожалуйста, введите имя пользователя'),
            'invalid': _('Неверное имя пользователя или пароль')
        }
    )
    
    password = forms.CharField(
        label=_("Password"),
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
        'inactive': _("Этот аккаунт неактивен."),
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Удаляем help_text для username
        self.fields['username'].help_text = None

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'birth_date', 'city', 'password')   #, 'profile_picture'