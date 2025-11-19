from datetime import datetime, timedelta
import json
from venv import logger
from django.http import JsonResponse
from ..utils import read_files



def process_city(request):
    cities = read_files('cities')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            city = data.get('city')
            city = city#.capitalize()
            # print(city)
            cit = [row["Город"] for row in cities]
            if city in cit:
                row_cit = [row for row in cities if row["Город"]==city][0]
                long = row_cit["Долгота"]
                hours = int(long//15)
                minutes = int(round((long/15 - hours)*60))

                utc = int(row_cit["Часовой пояс"])

                CURRENT_TIME = (datetime.utcnow() + timedelta(hours=utc)).time().strftime('%H:%M')
                CURRENT_TIME_SOLAR = (datetime.utcnow() + timedelta(hours=hours, minutes=minutes)).time().strftime('%H:%M')           
            else:
                f"Город {city} отсутствует в списке."

            result = {
                'success': True,
                'admin_time': CURRENT_TIME,
                'solar_time':CURRENT_TIME_SOLAR,
                'current_time': CURRENT_TIME_SOLAR,
                'city': f"Выбран город: {city}"
            }
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
def city_search(request):
    """API для поиска городов"""
    try:
        query = request.GET.get('q', '').strip().lower()
        
        # Загружаем города из файла
        cities = read_files('cities')
        
        # Получаем список всех городов
        all_cities = [row["Город"] for row in cities]
        
        # Если запрос пустой, возвращаем пустой список или все города
        if not query:
            # Можно вернуть пустой список или первые N городов
            # return JsonResponse([], safe=False, json_dumps_params={'ensure_ascii': False})
            return JsonResponse(all_cities, safe=False, json_dumps_params={'ensure_ascii': False})
        
        # Фильтрация (регистронезависимый поиск подстроки)
        filtered_cities = [
            city for city in all_cities 
            if query in city.lower()
        ][:15]  # Лимит результатов
        
        return JsonResponse(filtered_cities, safe=False, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        # Логируем ошибку
        logger.error(f"City search error: {str(e)}")
        # Возвращаем пустой список в случае ошибки
        return JsonResponse([], safe=False)