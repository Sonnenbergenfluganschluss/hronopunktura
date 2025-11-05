import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from ..utils import highlight_words, read_files



def process_our_date(request):
    calendar = read_files('calendar')
    cicle = read_files('cicle')
    seasons = read_files('seasons')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            our_date = data.get('ourdate')
            our_date_date = datetime.strptime(our_date, '%Y-%m-%d')
            get_our_date = [row for row in calendar if row['date'] == our_date_date.date().strftime('%Y-%m-%d')][0]
            if datetime.strptime(our_date, '%Y-%m-%d').date() < datetime.strptime(seasons[2][str(datetime.strptime(our_date, '%Y-%m-%d').year)], '%Y-%m-%d').date():
                year_o = [row for row in calendar if row['date'] == (our_date_date-timedelta(days=51)).date().strftime('%Y-%m-%d')][0]['years']
            else:
                year_o = get_our_date['years']

            mo = get_our_date['months']
            if our_date_date.date() < datetime.strptime([row for row in seasons if row['Месяц'] == mo.split()[0]][0][our_date[:4]], '%Y-%m-%d').date():
                month_o = [row for row in calendar if row['date'] == (our_date_date-timedelta(days=21)).date().strftime('%Y-%m-%d')][0]['months']
            else:
                month_o = get_our_date['months']
            day_o = get_our_date['days']

            day_iero = [row for row in cicle if row['Название_calendar'] == day_o][0]["Иероглиф"]
            month_iero = [row for row in cicle if row['Название_calendar'] == month_o][0]["Иероглиф"]
            year_iero = [row for row in cicle if row['Название_calendar'] == year_o][0]["Иероглиф"]

            birth_dayo = [row for row in cicle if row["Название_calendar"] == day_o][0]["Название_Русский"]
            birth_mono = [row for row in cicle if row["Название_calendar"] == month_o][0]["Название_Русский"]
            birth_yeao = [row for row in cicle if row["Название_calendar"] == year_o][0]["Название_Русский"]
            
            
            styled_df_o = f'''<table>
                                    <tr>
                                        <th> День </th>
                                        <th> Месяц </th>
                                        <th> Год </th>
                                    </tr>
                                    <tr>
                                        <td>{highlight_words(birth_dayo)}</td>
                                        <td>{highlight_words(birth_mono)}</td>
                                        <td>{highlight_words(birth_yeao)}</td>
                                    </tr>
                                    <tr>
                                        <td>{highlight_words(day_iero)}</td>
                                        <td>{highlight_words(month_iero)}</td>
                                        <td>{highlight_words(year_iero)}</td>
                                    </tr>                                   
                                </table>'''

            # Инь-ян
            in_yan_day = [row for row in cicle if row['Название_calendar'] == day_o][0]['инь_ян']
        
            # Определяем сезон по дате
            if (our_date_date < datetime.strptime(seasons[0][str(our_date_date.year)], '%Y-%m-%d')) or (our_date_date >= datetime.strptime(seasons[23][str(our_date_date.year)], '%Y-%m-%d')):
                season = seasons[23]
                n_season = seasons[23]['Сезон']
            else:
                for d in range(23):
                    if (our_date_date >= datetime.strptime(seasons[d][str(our_date_date.year)], '%Y-%m-%d')) & (our_date_date < datetime.strptime(seasons[d+1][str(our_date_date.year)], '%Y-%m-%d')):
                        season = seasons[d]
                        n_season = seasons[d]['Сезон']
                        break
            
            # Определяем день недели
            dow_dict = {0:"Понедельник", 1:"Вторник", 
                    2:"Среда", 3:"Четверг",
                    4:"Пятница", 5:"Суббота", 6:"Воскресенье"}

            # Планета-покровитель
            planets = read_files('planets')
            planet = [row for row in planets if row['День_недели']==our_date_date.weekday()][0]['Планета']
        
            # Цзя Цзы
            zya_zy = [row for row in cicle if row['Название_calendar'] == day_o][0]['Цзя_Цзы']

            day_sky_veto = read_files("day_sky_veto")
            ses = [row for row in day_sky_veto if row['сезон']==n_season][0]
            if ((day_iero[0]=='戊') or (day_iero[0]=='己')) and ((zya_zy==ses['ЦзяЦзы1']) or (zya_zy==ses['ЦзяЦзы2'])):
                str_veto = f"\
                    <br>1. <span style='color: red;'>{ses['ЗАПРЕТЫ']}</span> \
                    <br>2. <span style='color: red;'>Точки инь и ян каналов в области живота (ниже диафрагмы)</span>"
            elif (day_iero[0]=='戊') or (day_iero[0]=='己'):
                str_veto = "<span style='color: red;'>Точки инь и ян каналов в области живота (ниже диафрагмы)</span>"
            elif (zya_zy==ses['ЦзяЦзы1']) or (zya_zy==ses['ЦзяЦзы2']):
                str_veto = f"<span style='color: red;'>{ses['ЗАПРЕТЫ']}</span>"
            else:
                str_veto = "<span style='color: #3d7945;'>Запрета нет.</span>"
            
            veto = read_files('veto')
            sky_hands = read_files('sky_hands')
            earth_legs = read_files('earth_legs')
            str_result = f"<div><p>День: <span style='font-weight: bold;'>{in_yan_day.capitalize()}</span>\
                        <br>ЦзяЦзы дня: № <span style='font-weight: bold; color: #1e88e5;'>{zya_zy}</span>\
                        <br>Точки 24 Сезонов (Жэнь май): <span style='color: #1e88e5;'>{season['Символ']} || {season['Название']} || {season['Точки_Жэнь_май']} || {season['Название_точки']}</span>\
                        <br>День недели: <span style='font-weight: bold;'>{dow_dict[our_date_date.weekday()]}</span>\
                        <br>Планета-покровитель: <span style='color: #3d7945; font-weight: bold;'>{planet.capitalize()}</span>\
                        <br><span style='font-style: italic;'>Запрет по 4 сезонам:</span> <span style='font-weight: bold;'>{[row for row in veto if row['месяц']==month_iero[1]][0]['запрет']}</span>\
                        <br><span style='font-style: italic;'>Запреты на ручные каналы:</span>\
                          <br><span style='font-weight: bold; color: red;'>{[row for row in sky_hands if row['Иероглиф']==day_iero[0]][0]['канал']}</span>, \
                                <span style='font-weight: bold;'>{[row for row in sky_hands if row['Иероглиф']==day_iero[0]][0]['сторона_тела']} сторона:  пять точек транспортировки и точки между ними (до локтя)</span>\
                        <br><span style='font-style: italic;'>Запреты на ножные каналы:</span>\
                        <br><span style='font-weight: bold; color: red;'>{[row for row in earth_legs if row['Иероглиф']==month_iero[1]][0]['канал']}</span>, \
                                <span style='font-weight: bold; '>{[row for row in earth_legs if row['Иероглиф']==month_iero[1]][0]['сторона_тела']} сторона: пять точек транспортировки и точки между ними (до колена)</span>\
                        <br><span style='font-style: italic;'>Дни небесного запрета:</span> {str_veto}</p></div>"
            
            result = {
                'success': True,
                'our_date_result': our_date,
                'day_iero': day_iero,
                'our_date_table': styled_df_o,
                'str_result': str_result,
            }
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})