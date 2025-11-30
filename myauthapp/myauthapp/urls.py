from django.contrib import admin
from django.urls import path
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('application.urls')),
    path('', include('accounts.urls')),
    path('payments/', include('payments.urls')),
    path('week_prediction/', include('week_prediction.urls')),
    path('subscription/', include('subscription.urls')),
]