from datetime import datetime
import json
import logging
import re
from django.http import JsonResponse
from ..constants import color_dict, vis_yaer
from ..utils import highlight_words, read_files
from .methods.moon_palace import get_moon_palace
from .methods.feitenbafa import get_feiten
from .methods.linguibafa import get_lingui
from .methods.taiyanbafa import get_taiyan
from .methods.dasyao import get_dasyao


# Настройка логгера
logger = logging.getLogger(__name__)

        

def process_method(request):
    pass
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            our_date = data.get('our_date')
            our_date = datetime.strptime(our_date, '%Y-%m-%d').date()
            day_iero = data.get('day_iero')
            CURRENT_TIME_SOLAR = data.get('current_time')
            method_index = int(data.get('methodIndex'))
            methods = [" ", "ЛУННЫЕ ДВОРЦЫ", "ФЭЙ ТЭН БА ФА", 
                      "ЛИН ГУЙ БА ФА", "ТАЙ ЯН БА ФА", 
                      "ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА"]
            selected_method = methods[method_index]
            request.session['current_method'] = selected_method

            
           
            def calculate_method(selected_method, our_date = our_date, day_iero=day_iero):
                method = selected_method
                feitenbafa = read_files('feitenbafa')
                for_feitenbafa = read_files('for_feitenbafa')

                for x in range(12):
                    new=[row for row in for_feitenbafa if row['Иероглиф']==feitenbafa[x][day_iero[0]]][0]
                    feitenbafa[x].update(new)
                    
                current_hour = int(re.search(r"(\d*)", CURRENT_TIME_SOLAR)[0])

                if (current_hour == 23) or (current_hour == 0):
                    current_hour_china_list = feitenbafa[0]
                else:
                    for h in range(1,12):
                        if (current_hour >= (feitenbafa[h]['Время_int'])) & (current_hour < (feitenbafa[h]['Время_int']+2)):
                            current_hour_china_list = feitenbafa[h]
                            break

                current_hour_china = [current_hour_china_list['Иероглиф_ЗВ'], current_hour_china_list['Время'], current_hour_china_list['Канал'], current_hour_china_list['Точки']]
                
                headOfT = ""
                timeOfT = ""
                style_column = ""
                for row in feitenbafa:
                    if row["Иероглиф_ЗВ"] == current_hour_china[0]:
                        style_column = " style='background-color: yellow;'"
                    else:
                        style_column = ""
                    headOfT += f"<th{style_column}> <span style='color:{color_dict[row['Иероглиф_ЗВ']]};font-weight: bold'>{row['Иероглиф_ЗВ']}</span> </th>"
                    timeOfT += f"<td{style_column}> {highlight_words(row['Время'])} </td>"                
                                

                
                if method=="ЛУННЫЕ ДВОРЦЫ":
                    return get_moon_palace(our_date, vis_yaer)

                elif method=="ФЭЙ ТЭН БА ФА":   
                    return get_feiten(feitenbafa, current_hour_china, headOfT, timeOfT)             

                elif method=="ЛИН ГУЙ БА ФА":
                    return get_lingui(feitenbafa, day_iero, current_hour_china, headOfT, timeOfT)
    
                elif method=="ТАЙ ЯН БА ФА":
                    return get_taiyan(our_date, day_iero, CURRENT_TIME_SOLAR, headOfT, timeOfT)
               
                elif method=="ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА":
                    return get_dasyao(current_hour_china, headOfT, timeOfT)
                
                
            result = calculate_method(selected_method)  
            
            return JsonResponse({
                'success': True,
                'method': selected_method,
                'result': result
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})