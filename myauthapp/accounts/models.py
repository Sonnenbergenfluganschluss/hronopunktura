from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Добавляем дополнительные поля
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    city = models.CharField(max_length=50, blank=True)

    def get_date(self):
        if self.birth_date:
            day = self.birth_date.day
            month = self.birth_date.month
            year = self.birth_date.year
            if day<10:
                return f"{year}-{month}-0{day}"
            else:
                return f"{year}-{month}-{day}"
        else:
            return ""


    def __str__(self):
        return self.username
    