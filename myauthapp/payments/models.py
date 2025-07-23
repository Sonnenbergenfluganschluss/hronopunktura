from django.db import models
from accounts.models import CustomUser  # предполагая, что у вас есть кастомная модель пользователя

class Tariff(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default='RUB')
    duration_days = models.IntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.tariff.name}"

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    payment_id = models.CharField(max_length=100)
    yookassa_payment_id = models.CharField(max_length=100)  # ID платежа в ЮKassa
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Платёж № {self.id}  от  {self.user.username  if  self.user else 'Нет пользователя'}"