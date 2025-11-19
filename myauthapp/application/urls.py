from django.urls import path
from . import views
from .for_views.calculate.process_luo_taiyan import process_luo_taiyan

from .views import (
    home,
    process_birthday, process_city, process_our_date, process_method, city_search,
)

urlpatterns = [ 
     path('', views.home, name='home'),
     path('process_birthday/', views.process_birthday, name='process_birthday'),
     path('city_search/', views.city_search, name='city_search'),
     path('process_city/', views.process_city, name='process_city'),
     path('process_our_date/', views.process_our_date, name='process_our_date'),
     path('process_method/', views.process_method, name='process_method'),
     path('city-search/', views.city_search, name='city_search'),
     path('process-luo-taiyan/', process_luo_taiyan, name='process_luo_taiyan'),
]