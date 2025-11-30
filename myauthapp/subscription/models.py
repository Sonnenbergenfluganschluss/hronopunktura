from django.db import models
from accounts.models import CustomUser

class SubscriptionRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает'),
            ('approved', 'Одобрена'),
            ('rejected', 'Отклонена')
        ],
        default='pending'
    )
    
    def __str__(self):
        return f"Подписка {self.user.username}"