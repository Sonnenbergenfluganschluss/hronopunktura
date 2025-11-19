from datetime import datetime
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import read_files

@login_required
def home(request):
    """Главная страница"""
    cities = read_files('cities')
    cit = [row["Город"] for row in cities]
    methods = [" ", "ЛУННЫЕ ДВОРЦЫ", "ФЭЙ ТЭН БА ФА", "ЛИН ГУЙ БА ФА", 
               "ТАЙ ЯН БА ФА", "ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА"]
    
    context = {
        'title': 'Главная',
        'current_date_show': datetime.now().strftime("%d.%m.%Y"),
        'current_date': datetime.now().strftime("%Y-%m-%d"),
        'cities_json': json.dumps(cit), 
        'methods': methods,
    }
    return render(request, 'application/home.html', context)