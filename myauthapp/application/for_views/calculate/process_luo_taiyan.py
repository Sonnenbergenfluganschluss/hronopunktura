import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .methods.taiyanbafa import get_luo_taiyan, get_current_channel
from .methods.linguibafa import get_current_channel_lingui
from .methods.feitenbafa import get_current_channel_feiten

@login_required
@csrf_exempt
def process_luo_taiyan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            needed_channel = data.get('needed_channel')
            # Получаем current_channel из глобальной переменной
            current_method = request.session.get('current_method')
            if current_method == "ФЭЙ ТЭН БА ФА":
                current_channel = get_current_channel_feiten()
            elif current_method == "ЛИН ГУЙ БА ФА":
                current_channel = get_current_channel_lingui()
            elif current_method == "ТАЙ ЯН БА ФА":
                current_channel = get_current_channel()
            

            # Вычисляем результат
            result = get_luo_taiyan(current_channel, needed_channel)

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