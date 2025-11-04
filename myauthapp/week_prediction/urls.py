from django.urls import path
from . import views


app_name = 'week_prediction'  # Это определяет namespace

urlpatterns = [
    path('', views.week_prediction, name='week_prediction'),
    path('predictions-process/', views.predictions_process, name='predictions_process'),
]