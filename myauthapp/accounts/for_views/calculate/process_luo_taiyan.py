import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .methods.taiyanbafa import get_luo_taiyan, get_current_row

@login_required
@csrf_exempt
def process_luo_taiyan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            needed_channel = data.get('needed_channel')
            print('needed_channel: ',needed_channel)
            # Получаем current_row из глобальной переменной
            current_row = get_current_row()
            print('current_row: ', current_row)
            # Вычисляем результат
            result = get_luo_taiyan(current_row, needed_channel)
            print('result: ', result)
            return JsonResponse({
                'success': True,
                'result': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})