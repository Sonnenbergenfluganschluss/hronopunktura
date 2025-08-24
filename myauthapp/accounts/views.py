# from asyncio.log import logger
import json
# import pandas as pd
from datetime import datetime, timedelta, date
import re
import os
from itertools import cycle
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse  # если нужен AJAX
from .forms import CustomUserCreationForm, CustomUserChangeForm
from payments.models import Tariff

# Настройка логгера
logger = logging.getLogger(__name__)


animal = ["крыса", "бык", "тигр", "кролик", "дракон", "змея", "лошадь", "коза", "обезьяна", "петух", "собака", "свинья"]
stihiya = ["дерево", "дерево", "огонь", "огонь", "почва", "почва", "металл", "металл", "вода", "вода"]
in_yan = ["ян", "инь"]

vis_yaer = [1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968, 
            1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 
            2024, 2028, 2032, 2036, 2040, 2044, 2048, 2052]

moon_palace = dict({1: [1920, 1942, 0, 1987, 2009, 2032], 2: [0, 1943, 1965, 1988, 2010, 0], 
    3: [1921, 1944, 1966, 0, 2011, 2033], 4: [1922, 0, 1967, 1989, 2012, 2034], 
    5: [1923, 1945, 1968, 1990, 0, 2035], 6: [1924, 1946, 0, 1991, 2013, 2036], 
    7: [0, 1947, 1969, 1992, 2014, 0], 8: [1925, 1948, 1970, 0, 2015, 2037], 
    9: [1926, 0, 1971, 1993, 2016, 2038], 10: [1927, 1949, 1972, 1994, 0, 2039], 
    11: [1928, 1950, 0, 1995, 2017, 2040], 12: [0, 1951, 1973, 1996, 2018, 0], 
    13: [1929, 1952, 1974, 0, 2019, 2041], 14: [1930, 0, 1975, 1997, 2020, 2042], 
    15: [1931, 1953, 1976, 1998, 0, 2043], 16: [1932, 1954, 0, 1999, 2021, 2044], 
    17: [0, 1955, 1977, 2000, 2022, 0], 18: [1933, 1956, 1978, 0, 2023, 2045], 
    19: [1934, 0, 1979, 2001, 2024, 2046], 20: [1935, 1957, 1980, 2002, 0, 2047], 
    21: [1936, 1958, 0, 2003, 2025, 2048], 22: [0, 1959, 1981, 2004, 2026, 0], 
    23: [1937, 1960, 1982, 0, 2027, 2049], 24: [1938, 0, 1983, 2005, 2028, 2050], 
    25: [1939, 1961, 1984, 2006, 0, 2051], 26: [1940, 1962, 0, 2007, 2029, 2052], 
    27: [0, 1963, 1985, 2008, 2030, 0], 28: [1941, 1964, 1986, 0, 2031, 2053]})

sec_step = {1:27, 2:2, 3:2, 4:5, 5:7, 6:10, 7:12, 8:15, 9:18, 10:20, 11:23, 12:25}


man = ["Liv.1", "Liv.4", "Liv.3", "Gb.37/Liv.3", "Liv.5/Gb.40", "Liv.2", "Liv.8", 
    "Kid.1", "Kid.7", "Kid.3", "Bl.58/Kid.3", "Kid.4/Bl.64", "Kid.2", "Kid.10", 
    "Lu.11", "Lu.8", "Lu.9", "Co.6/Lu.9", "Co.4/Lu.7", "Lu.10", "Lu.5", 
    "Ht.9/Hg.9", "Ht.4/Hg.5", "Ht.7/Hg.7", "Si.7/Ht.7/Hg.7", 
    "Ht.5/Hg.6/Si.4", "Ht.8/Hg.8", "Ht.3/ Hg.3"]

woman = ["Gb.41", "Gb.44", "Gb.34", "Gb.37/Liv.3", "Liv.5/Gb.40", "Gb.38", "Gb.43", 
    "Bl.65", "Bl.67", "Bl.40", "Bl.58/Kid.3", "Kid.4/Bl.64", "Bl.60", "Bl.66", 
    "Co.3", "Co.1", "Co.11", "Co.6/Lu.9", "Co4/Lu.7", "Co.5", "Co.2", 
    "Si.3", "Si.1", "Si.8", "Si.7/Ht.7/Hg.7", "Ht.5/Hg.6/Si.4", "Si.5", "Si.2"]

orange = '#ad5c0a'

color_dict = {'甲':'green', '乙':'green', '丙':'red', '丁':'red', '戊':f'{orange}', '己':f'{orange}', '庚':'grey', '辛':'grey', '壬':'blue', '癸':'blue',
                '子':'blue', '丑':f'{orange}', '寅':'green', '卯':'green', '辰':f'{orange}', '巳':'red', '午':'red', '未':f'{orange}', '申':'grey', '酉':'grey', '戌':f'{orange}', '亥':'blue'}

color_dict_earth = {'子':'blue', '丑':f'{orange}', '寅':'green', '卯':'green', '辰':f'{orange}', '巳':'red', '午':'red', '未':f'{orange}', '申':'grey', '酉':'grey', '戌':f'{orange}', '亥':'blue'}

def read_files(table_name):
    with open(f"accounts/data/{table_name}.json", encoding='utf-8') as f: # Открываем файл и связываем его с объектом "f"
        table = json.load(f)
    return table

def get_month(our_date):
    stih = cycle(stihiya)
    anim = cycle(animal)
    inyan = cycle(in_yan)  
    start_month = date(1924, 1, 1)
    end_months=(our_date.year-start_month.year)*12 + our_date.month + 1
    lst = []
    for i in range(end_months):
        lst.append(f"{next(anim)} {next(inyan)} {next(stih)}".capitalize())
    return lst[-1]


# Функция для окрашивания отдельных слов
def highlight_words(text):
    highlighted_text = text
    if text[0] in color_dict.keys():
        highlighted_text = text.replace(text[0], f'<span style="color:{color_dict[text[0]]};font-weight: bold">{text[0]}</span>')
        highlighted_text = highlighted_text.replace(text[1], f'<span style="color:{color_dict[text[1]]};font-weight: bold">{text[1]}</span>')
    else:
        highlighted_text = text.strip()
        highlighted_text = text.replace("  ", " ")
        highlighted_text = text.replace(" ", "<br>")
    return highlighted_text




@login_required
def home(request):
    cities = read_files('cities')
    cit = [row["Город"] for row in cities]
    methods = [" ", "ЛУННЫЕ ДВОРЦЫ", "ФЭЙ ТЭН БА ФА", "ЛИН ГУЙ БА ФА", 
               "ТАЙ ЯН БА ФА", "ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА"]
    context = {
        'title': 'Главная',
        'current_date_show': datetime.now().strftime("%d.%m.%Y"),
        'current_date': datetime.now().strftime("%Y-%m-%d"),
        'cities_json': json.dumps(cit), 
        'methods': methods, # Добавьте другие переменные, которые нужно передать в шаблон
    }
    return render(request, 'accounts/home.html', context)


def process_birthday(request):
    calendar = read_files('calendar')
    cicle = read_files('cicle')
    seasons = read_files('seasons')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            birthday = data.get('birthday')
            birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
            get_birthday = [row for row in calendar if row['date'] == birthday_date.date().strftime('%Y-%m-%d')][0]

            if datetime.strptime(birthday, '%Y-%m-%d').date() < datetime.strptime(seasons[2][str(datetime.strptime(birthday, '%Y-%m-%d').year)], '%Y-%m-%d').date():
                year_v = [row for row in calendar if row['date'] == (birthday_date-timedelta(days=51)).date().strftime('%Y-%m-%d')][0]['years']
            else:
                year_v = get_birthday['years']

            mv = get_birthday['months']
            if birthday_date.date() < datetime.strptime([row for row in seasons if row['Месяц'] == mv.split()[0]][0][birthday[:4]], '%Y-%m-%d').date():
                month_v = [row for row in calendar if row['date'] == (birthday_date-timedelta(days=21)).date().strftime('%Y-%m-%d')][0]['months']
            else:
                month_v = get_birthday['months']
            day_v = get_birthday['days']

            day_ier = [row for row in cicle if row['Название_calendar'] == day_v][0]["Иероглиф"]
            month_ier = [row for row in cicle if row['Название_calendar'] == month_v][0]["Иероглиф"]
            year_ier = [row for row in cicle if row['Название_calendar'] == year_v][0]["Иероглиф"]

            birth_day = [row for row in cicle if row["Название_calendar"] == day_v][0]["Название_Русский"]
            birth_mon = [row for row in cicle if row["Название_calendar"] == month_v][0]["Название_Русский"]
            birth_yea = [row for row in cicle if row["Название_calendar"] == year_v][0]["Название_Русский"]
            
            
            styled_df_b = f'''<table>
                                    <tr>
                                        <th> День </th>
                                        <th> Месяц </th>
                                        <th> Год </th>
                                    </tr>
                                    <tr>
                                        <td>{highlight_words(birth_day)}</td>
                                        <td>{highlight_words(birth_mon)}</td>
                                        <td>{highlight_words(birth_yea)}</td>
                                    </tr>
                                    <tr>
                                        <td>{highlight_words(day_ier)}</td>
                                        <td>{highlight_words(month_ier)}</td>
                                        <td>{highlight_words(year_ier)}</td>
                                    </tr>                                   
                                </table>'''
            
            result = {
                'success': True,
                'birthday_result': birthday,
                'birthday_table': styled_df_b
            }
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def process_city(request):
    cities = read_files('cities')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            city = data.get('city')
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
    cities = read_files('cities')
    try:
        query = request.GET.get('q', '').strip().lower()
       
        # 1. Получаем список городов из контекста (можно заменить на cache/db)
        cit = [row["Город"] for row in cities]
        
        # 2. Фильтрация (регистронезависимый поиск подстроки)
        filtered = [
            city for city in cit 
            if query in city.lower()
        ]  # Лимит результатов
        
        # 3. Возвращаем JSON (отключаем ASCII-кодирование для кириллицы)
        return JsonResponse(filtered, safe=False, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        # Логируем ошибку и возвращаем пустой список
        import logging
        logging.error(f"City search error: {str(e)}")
        return JsonResponse([], safe=False)


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
            print(get_our_date)
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
                    \n1 <span style='color: red;'>{ses['ЗАПРЕТЫ']}</span> \
                    \n2 <span style='color: red;'>Точки инь и ян каналов в области живота (ниже диафрагмы)</span>"
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
                        \n<br>ЦзяЦзы дня: № <span style='font-weight: bold; color: #1e88e5;'>{zya_zy}</span>\
                        # \n<br>Точки 24 Сезонов (Жэнь май): <span style='color: #1e88e5;'>{season['Символ']} || {season['Название']} || {season['Точки_Жэнь_май']} || {season['Название_точки']}</span>\
                        \n<br>День недели: <span style='font-weight: bold;'>{dow_dict[our_date_date.weekday()]}</span>\
                        \n<br>Планета-покровитель: <span style='color: #3d7945; font-weight: bold;'>{planet.capitalize()}</span>\
                        \n<br><span style='font-style: italic;'>Запрет по 4 сезонам:</span> <span style='font-weight: bold;'>{[row for row in veto if row['месяц']==month_iero[1]][0]['запрет']}</span>\
                        \n<br><span style='font-style: italic;'>Запреты на ручные каналы:</span>\
                        \n  <br><span style='font-weight: bold; color: red;'>{[row for row in sky_hands if row['Иероглиф']==day_iero[0]][0]['канал']}</span>, \
                                <span style='font-weight: bold;'>{[row for row in sky_hands if row['Иероглиф']==day_iero[0]][0]['сторона_тела']} сторона:  пять точек транспортировки и точки между ними (до локтя)</span>\
                        \n<br><span style='font-style: italic;'>Запреты на ножные каналы:</span>\
                        \n  <br><span style='font-weight: bold; color: red;'>{[row for row in earth_legs if row['Иероглиф']==month_iero[1]][0]['канал']}</span>, \
                                <span style='font-weight: bold; '>{[row for row in earth_legs if row['Иероглиф']==month_iero[1]][0]['сторона_тела']} сторона: пять точек транспортировки и точки между ними (до колена)</span>\
                        \n<br><span style='font-style: italic;'>Дни небесного запрета:</span> {str_veto}</p></div>"
            
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

                    import base64
                    from PIL import Image
                    from io import BytesIO


                    def get_thumbnail(path):
                        i = Image.open(path)    
                        return i


                    def image_base64(im):
                        if isinstance(im, str):
                            im = get_thumbnail(im)
                        with BytesIO() as buffer:
                            im.save(buffer, 'png')
                            return base64.b64encode(buffer.getvalue()).decode()

                    def image_formatter(im):
                        return f'<img src="data:image/png; base64,{image_base64(im)}" style="width: 30%; display: block; margin: 0 auto;">'

                    path_yan = 'accounts/data/images/yan.jpg'
                    path_in = 'accounts/data/images/in.jpg'

                    for k, v in moon_palace.items():
                        if our_date.year in v:
                            first_step = k
                    if (our_date.year in vis_yaer) & (our_date > datetime.strptime(f"{our_date.year}-02-28", "%Y-%m-%d").date()):
                        first_step = first_step+1
                    lunar_day = first_step + sec_step[our_date.month]+ our_date.day

                    moon_palace_df = read_files('moonPalace')
                    while lunar_day > 28:
                        lunar_day+=-28
                    if lunar_day in range(1, 15):
                        lunar_day_ton = lunar_day+14
                    else:
                        lunar_day_ton = lunar_day-14
                    row_ld = [row for row in moon_palace_df if row["Лунный_день"]==lunar_day][0]
                    symbol = row_ld["Иероглиф"]
                    val = row_ld["Созвездие"]
                    point = row_ld["Точка_Ду_май"] + "||" + row_ld["Название"]
                 
                    return f''' 
                        <div>
                            <div>
                                Лунная стоянка: <span style='font-weight: bold;'>{str(lunar_day)}</span> <span style='font-weight: bold; color: red;'>{symbol}</span> <span style='font-weight: bold;'>{val.capitalize()}</span> 
                                <br>Точки 28 Лунных Стоянок (Ду май): <span style='font-weight: bold;'>{point}</span> 
                                <br>
                                <br><span style='font-style: italic;'>Техника 28 Лунных Стоянок</span>
                                <br>Помочь выйти событию (седирование)
                                <div class='table_moon_palace'>
                                    <table>
                                        <tr>
                                            <th> Помочь выйти событию (седирование) </th>
                                            <th> Точки </th>
                                        </tr>
                                        <tr>
                                            <td>{image_formatter(get_thumbnail(path_yan))}</td>
                                            <td>{man[lunar_day-1]}</td>
                                        </tr>
                                        <tr>
                                            <td>{image_formatter(get_thumbnail(path_in))}</td>
                                            <td>{woman[lunar_day-1]}</td>
                                        </tr>
                                    </table>
                                </div>
                                <br>Заставить выйти событие (тонизация)
                                <div class='table_moon_palace'>
                                    <table>
                                        <tr>
                                            <th> Заставить выйти событие (тонизация) </th>
                                            <th> Точки </th>
                                        </tr>
                                        <tr>
                                            <td>{image_formatter(get_thumbnail(path_yan))}</td>
                                            <td>{man[lunar_day_ton-1]}</td>
                                        </tr>
                                        <tr>
                                            <td>{image_formatter(get_thumbnail(path_in))}</td>
                                            <td>{woman[lunar_day_ton-1]}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                        '''

                elif method=="ФЭЙ ТЭН БА ФА":                    
                    channelOfT = ""
                    pointsOfT = ""
                    for row in feitenbafa:
                        if row["Иероглиф_ЗВ"] == current_hour_china[0]:
                            style_column = " style='background-color: yellow;'"
                        else: 
                            style_column = ""
                        channelOfT += f"<td{style_column}> {highlight_words(row['Канал'])} </td>"
                        pointsOfT += f"<td{style_column}> {highlight_words(row['Точки'])} </td>"

                        table = f'''
                            <div>
                                <table>
                                    <tr>
                                        {headOfT}
                                    </tr>
                                    <tr>
                                        {timeOfT}
                                    </tr>
                                    <tr>
                                        {channelOfT}
                                    </tr>
                                    <tr>
                                        {pointsOfT}
                                    </tr>
                                </table>
                            </div>
                            '''
                    return table

                elif method=="ЛИН ГУЙ БА ФА":
                    for_lin_gui_ba_fa = read_files('forLinGuiBaFa')
                    sky_hands = read_files('sky_hands')
                    earth_legs = read_files('earth_legs')
                    resOfT = ""
                    channelOfT = ""
                    pointsOfT = ""
                    namessOfT = ""
                    for i in feitenbafa:
                        summ = [row for row in sky_hands if row['Иероглиф']==day_iero[0]][0]['i_day'] + \
                                    [row for row in sky_hands if row['Иероглиф']==i['Иероглиф']][0]['i_hour'] + \
                                    [row for row in earth_legs if row['Иероглиф']==day_iero[1]][0]['j_day'] + \
                                    [row for row in earth_legs if row['Иероглиф']==i['Иероглиф_ЗВ']][0]['j_hour']

                        cicle = read_files('cicle')
                        if [row for row in cicle if row['Иероглиф']==day_iero][0]['инь_ян'] == 'ян':
                            res = summ%9
                            if res == 0:
                                res = 9
                        else:
                            res = summ%6
                            if res == 0:
                                res = 6  
                        
                        linguibafa_row = [row for row in for_lin_gui_ba_fa if row['res']==res][0]

                        if i["Иероглиф_ЗВ"] == current_hour_china[0]:
                            style_column = " style='background-color: yellow;'"
                        else:
                            style_column = ""
                        resOfT += f"<td{style_column}> {res} </td>"
                        channelOfT += f"<td{style_column}> {highlight_words(linguibafa_row['0'])} </td>"
                        pointsOfT += f"<td{style_column}> {highlight_words(linguibafa_row['point'])} </td>"
                        namessOfT += f"<td{style_column}> {highlight_words(linguibafa_row['1'])} </td>"

                    table = f'''
                        <div>
                            <table>
                                <tr>
                                    {headOfT}
                                </tr>
                                <tr>
                                    {timeOfT}
                                </tr>
                                <tr>
                                    {resOfT}
                                </tr>
                                <tr>
                                    {channelOfT}
                                </tr>
                                <tr>
                                    {pointsOfT}
                                </tr>
                                <tr>
                                    {namessOfT}
                                </tr>
                            </table>
                        </div>
                        '''
                    return table
    
                elif method=="ТАЙ ЯН БА ФА":
                    list_tai = os.listdir("accounts/data/taiYanBaFa/")
                    for l in list_tai:
                        if day_iero[0] in l:
                            file=re.findall(f'(\w*{day_iero[0]}\w*)', l)
                    tai_yan_ba_fa = read_files(f"taiYanBaFa/{file[0]}")
                    
                    d = int(our_date.day)
                    m = int(our_date.month)
                    y = int(our_date.year)
                    h = int(CURRENT_TIME_SOLAR.split(":")[0])
                    mi = int(CURRENT_TIME_SOLAR.split(":")[1])

                    current_time_solar = datetime(y, m, d, h, mi).time()
                    
                    row_tab = ""
                    for row in tai_yan_ba_fa:
                        start_time = datetime(y, m, d, hour=int(row['1'].split(" - ")[0].split(".")[0]), minute=int(row['1'].split(" - ")[0].split(".")[1])).time()
                        end_time = datetime(y, m, d, hour=int(row['1'].split(" - ")[1].split(".")[0]), minute=int(row['1'].split(" - ")[1].split(".")[1])).time()
                        # style_column = ""
                        if (current_time_solar >= start_time) & (current_time_solar < end_time):
                            style_column = " id='x-row' style='background-color: yellow;'"
                        else:
                            style_column = ""

                        row_tab += f'''
                            <tr{style_column}>
                                <td> <span style='color:{color_dict[row['0']]};font-weight: bold'>{row['0']}</span> </td>
                                <td> {row['1']} </td>
                                <td> {highlight_words(row['2'])} </td>
                                <td> {highlight_words(row['3'])} </td>
                                <td> {highlight_words(row['4'])} </td>
                                <td> {highlight_words(row['5'])} </td>
                            </tr>
                        '''

                        table = f'''
                            <div class=".scrollable-table;" style="height: 300px; overflow: auto;">
                                <table>
                                    {row_tab}
                                </table>
                            </div>
                            '''
                   
                    return table
               
                elif method=="ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА":
                    da_syao = read_files("da_syao")
                    # current_hour_china_list = da_syao[current_hour_china[1]].to_list()
                    # current_hour_china_str = ' || '.join(current_hour_china_list)
                    
                    channelOfT = ""
                    pointsOfT = ""
                    pointsOfT2 = ""
                    for row in da_syao:
                        if row["0"] == current_hour_china[0]:
                            style_column = " style='background-color: yellow;'"
                        else: 
                            style_column = ""
                        channelOfT += f"<td{style_column}> {highlight_words(row['2'])} </td>"
                        pointsOfT += f"<td{style_column}> {highlight_words(row['3'])} </td>"
                        pointsOfT2 += f"<td{style_column}> {highlight_words(row['4'])} </td>"

                        table = f'''
                            <div>
                                <table>
                                    <tr>
                                        {headOfT}
                                    </tr>
                                    <tr>
                                        {timeOfT}
                                    </tr>
                                    <tr>
                                        {channelOfT}
                                    </tr>
                                    <tr>
                                        {pointsOfT}
                                    </tr>
                                    <tr>
                                        {pointsOfT2}
                                    </tr>
                                </table>
                            </div>
                            '''
                    return table     
                
            result = calculate_method(selected_method)  # Замените на вашу функцию
            
            return JsonResponse({
                'success': True,
                'method': selected_method,
                'result': result
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})








def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} создан! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    active_tariff = Tariff.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль обновлен!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'active_tariff': active_tariff,
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)












def index(request):
    cities = read_files('cities')
    cit = cities["Город"].values.tolist()
    print("Cities before JSON:", cit[:10])
    methods = [" ", "ЛУННЫЕ ДВОРЦЫ", "ФЭЙ ТЭН БА ФА", "ЛИН ГУЙ БА ФА", 
               "ТАЙ ЯН БА ФА", "ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА"]
    context = {
        'title': 'Главная',
        'current_date_show': datetime.now().strftime("%d.%m.%Y"),
        'current_date': datetime.now().strftime("%Y-%m-%d"),
        'cities_json': json.dumps(cit), 
        'methods': methods, # Добавьте другие переменные, которые нужно передать в шаблон
    }
    return render(request, 'accounts/index.html', context)


