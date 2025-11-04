from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    # Добавляем дополнительные поля
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    city = models.CharField(max_length=50, blank=True)
    
    # Добавляем поля для верификации email
    email_verified = models.BooleanField(default=False, verbose_name='Email подтвержден')
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    def get_date(self):
        if self.birth_date:
            day = self.birth_date.day
            month = self.birth_date.month
            year = self.birth_date.year
            if day < 10:
                day = f'0{day}'
            if month < 10:
                month = f'0{month}'
            return f"{year}-{month}-{day}"
        else:
            return ""

    def is_verification_token_expired(self):
        """Проверяет, истек ли срок действия токена верификации"""
        if self.token_created_at is None:
            return True
        return timezone.now() > self.token_created_at + timedelta(hours=24)

    def generate_verification_token(self):
        """Генерирует новый токен верификации"""
        self.verification_token = uuid.uuid4()
        self.token_created_at = timezone.now()
        self.save()

    def verify_email(self, token):
        """Подтверждает email если токен верный и не истек"""
        if (self.verification_token == token and 
            not self.is_verification_token_expired()):
            self.email_verified = True
            self.verification_token = None
            self.token_created_at = None
            self.is_active = True  # Активируем пользователя
            self.save()
            return True
        return False

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'