# from asyncio.log import logger
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib import messages
from django.http import JsonResponse  # если нужен AJAX
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import re
import os
import pytz
from itertools import cycle
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

sky = {'甲': ':green[甲]',
        '乙': ':green[乙]',
        '丙': ':red[丙]',
        '丁': ':red[丁]',
        '戊': ':orange[戊]',
        '己': ':orange[己]',
        '庚': ':darkgray[庚]',
        '辛': ':darkgray[辛]',
        '壬': ':blue[壬]',
        '癸': ':blue[癸]'}

earth = {'子': ':blue[子]',
        '丑': ':orange[丑]',
        '寅': ':green[寅]',
        '卯': ':green[卯]',
        '辰': ':orange[辰]',
        '巳': ':red[巳]',
        '午': ':red[午]',
        '未': ':orange[未]',
        '申': ':darkgray[申]',
        '酉': ':darkgray[酉]',
        '戌': ':orange[戌]',
        '亥': ':blue[亥]'}

color_dict = {'甲':'green', '乙':'green', '丙':'red', '丁':'red', '戊':'orange', '己':'orange', '庚':'grey', '辛':'grey', '壬':'blue', '癸':'blue',
                '子':'blue', '丑':'orange', '寅':'green', '卯':'green', '辰':'orange', '巳':'red', '午':'red', '未':'orange', '申':'grey', '酉':'grey', '戌':'orange', '亥':'blue'}

color_dict_earth = {'子':'blue', '丑':'orange', '寅':'green', '卯':'green', '辰':'orange', '巳':'red', '午':'red', '未':'orange', '申':'grey', '酉':'grey', '戌':'orange', '亥':'blue'}


def local_css(file_name):
    with open(file_name) as f:
        print('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


def read_files(table_name):       
    table = pd.read_csv(f"accounts/data/{table_name}.csv")
    return table


def background(color):
    return np.where(f"color: {color};", None)

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
        highlighted_text = text.replace(" ", "<br>")
    return highlighted_text




@login_required
def home(request):
    cities = read_files('cities')
    cit = cities["Город"].values.tolist()
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

    calendar['date'] = pd.to_datetime(calendar['date'])
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            birthday = data.get('birthday')
            try:
                if pd.to_datetime(birthday) < pd.to_datetime(seasons.loc[2, str(pd.to_datetime(birthday).year)]):
                    year_v = calendar[calendar['date']==pd.to_datetime(pd.to_datetime(birthday)-timedelta(days=51))]['years'].values[0]
                else:
                    year_v = calendar[calendar['date']==pd.to_datetime(birthday)]['years'].values[0]

                mv = calendar[calendar['date']==pd.to_datetime(birthday)]['months'].values[0]
                if pd.to_datetime(birthday) < pd.to_datetime(seasons[seasons['Месяц']==mv.split()[0]][str(pd.to_datetime(birthday).year)].values[0]):
                    month_v = calendar[calendar['date']==pd.to_datetime(pd.to_datetime(birthday)-timedelta(days=21))]['months'].values[0]
                else:
                    month_v = calendar[calendar['date']==pd.to_datetime(birthday)]['months'].values[0]
                day_v = calendar[calendar['date']==pd.to_datetime(birthday)]['days'].values[0]
                day_ier = cicle[cicle["Название_calendar"] == day_v]["Иероглиф"].values[0]
                month_ier = cicle[cicle["Название_calendar"] == month_v]["Иероглиф"].values[0]
                year_ier = cicle[cicle["Название_calendar"] == year_v]["Иероглиф"].values[0]

                birthday_df = pd.DataFrame(columns=["День", "Месяц", "Год"], data=None)
                birthday_df["День"] = [
                    f"{cicle[cicle['Название_calendar'] == day_v]['Название_Русский'].values[0]}",
                    day_ier
                ]
                birthday_df["Месяц"] = [
                    f"{cicle[cicle['Название_calendar'] == month_v]['Название_Русский'].values[0]}",
                    month_ier
                ]
                birthday_df["Год"] = [
                    f"{cicle[cicle['Название_calendar'] == year_v]['Название_Русский'].values[0]}",
                    year_ier
                ]
                birthday_df['День'] = birthday_df['День'].apply(highlight_words)
                birthday_df['Месяц'] = birthday_df['Месяц'].apply(highlight_words)
                birthday_df['Год'] = birthday_df['Год'].apply(highlight_words)
                
                styled_df_b = birthday_df.to_html(
                        classes='table table-striped table-hover',
                        table_id='styled_df_b',
                        escape=False,
                        index=False,  # Не показывать индексы
                        justify='center'  # Выравнивание
                    )
            except:
                logger.error("Некорректная дата. Попробуйте снова")
            
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
            cit = cities["Город"].values.tolist()
            if city in cit:
                if len(cities[cities["Город"].str.contains(city, regex=True).fillna(False)]) != 0:
                        raw = cities[cities["Город"].str.contains(city, regex=True)][["Индекс", "Город", "Часовой пояс"]]
                else:
                    logger.error("Города нет в списке")

                id_city = raw.index
                long = cities.loc[id_city, "Долгота"].values[0]
                hours = int(long//15)
                minutes = int(round((long/15 - hours)*60))

                utc = int(raw["Часовой пояс"].values[0])

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
        cit = cities["Город"].values.tolist()
        
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
            # CURRENT_TIME_SOLAR = data.get('current_time')
            # print(CURRENT_TIME_SOLAR)
            our_date = data.get('ourdate')
            our_date = pd.to_datetime(our_date)

            d = int(our_date.day)

            if pd.to_datetime(our_date) < pd.to_datetime(seasons.loc[2, str(our_date.year)]):
                year_o = calendar[calendar['date']==pd.to_datetime(pd.to_datetime(our_date)-timedelta(days=51))]['years'].values[0]
            else:
                year_o = calendar[calendar['date']==pd.to_datetime(our_date)]['years'].values[0]

            mo = calendar[calendar['date']==pd.to_datetime(our_date)]['months'].values[0]
            if pd.to_datetime(our_date) < pd.to_datetime(seasons[seasons['Месяц']==mo.split()[0]][str(pd.to_datetime(our_date).year)].values[0]):
                month_o = calendar[calendar['date']==pd.to_datetime(pd.to_datetime(our_date)-timedelta(days=21))]['months'].values[0]
            else:
                month_o = calendar[calendar['date']==pd.to_datetime(our_date)]['months'].values[0]

            day_o = calendar[calendar['date']==pd.to_datetime(our_date)]['days'].values[0]
            day = cicle[cicle["Название_calendar"] == day_o]["Название_Русский"].values[0]
            day_iero = cicle[cicle["Название_calendar"] == day_o]["Иероглиф"].values[0]
            month_iero = cicle[cicle["Название_calendar"] == month_o]["Иероглиф"].values[0]
            year_iero = cicle[cicle["Название_calendar"] == year_o]["Иероглиф"].values[0]

            our_date_df = pd.DataFrame(columns=["День", "Месяц", "Год"])
            our_date_df["День"] = [
                f"{cicle[cicle['Название_calendar'] == day_o]['Название_Русский'].values[0]}",
                day_iero
            ]
            our_date_df["Месяц"] = [
                f"{cicle[cicle['Название_calendar'] == month_o]['Название_Русский'].values[0]}",
                month_iero
            ]
            our_date_df["Год"] = [
                f"{cicle[cicle['Название_calendar'] == year_o]['Название_Русский'].values[0]}",
                year_iero
            ]
            our_date_df['День'] = our_date_df['День'].apply(highlight_words)
            our_date_df['Месяц'] = our_date_df['Месяц'].apply(highlight_words)
            our_date_df['Год'] = our_date_df['Год'].apply(highlight_words)
            
            styled_df_o = our_date_df.style.hide(axis="index").set_table_attributes('style="width: 100%;"').to_html()

            # Инь-ян
            in_yan_day = cicle[cicle['Название_calendar'] == day_o]['инь_ян'].values[0]
        
            # Определяем сезон по дате
            if (pd.to_datetime(our_date) < pd.to_datetime(seasons[str(our_date.year)][0])) or (pd.to_datetime(our_date) >= pd.to_datetime(seasons[str(our_date.year)][23])):
                season = seasons.iloc[23][["Символ", "Название", "Точки_Жэнь_май",	"Название_точки"]].values
                n_season = seasons.iloc[23][['Сезон']].values[0]
            else:
                for d in range(23):
                    if (pd.to_datetime(our_date) >= pd.to_datetime(seasons[str(our_date.year)][d])) & (pd.to_datetime(our_date)<pd.to_datetime(seasons[str(our_date.year)][d+1])):
                        season = seasons.iloc[d][["Символ", "Название", "Точки_Жэнь_май",	"Название_точки"]].values
                        n_season = seasons.iloc[d][['Сезон']].values[0]
                        break
            
            # Определяем день недели
            dow_dict = {0:"Понедельник", 1:"Вторник", 
                    2:"Среда", 3:"Четверг",
                    4:"Пятница", 5:"Суббота", 6:"Воскресенье"}

            # Планета-покровитель
            planets = read_files('planets')
            planet = planets[planets['День_недели']==pd.to_datetime(our_date).day_of_week]['Планета'].values[0]
        
            # Цзя Цзы
            zya_zy = cicle[cicle['Название_calendar'] == day_o]['Цзя_Цзы'].values[0]

            # Запреты выводим:
            # Дни небесного запрета
            day_sky_veto = pd.read_csv("accounts/data/day_sky_veto.csv")
            id_v = day_sky_veto[day_sky_veto['сезон']==n_season].index
            if ((day_iero[0]=='戊') or (day_iero[0]=='己')) and ((zya_zy==day_sky_veto.iloc[id_v, 1].values[0]) or (zya_zy==day_sky_veto.iloc[id_v, 2].values[0])):
                str_veto = f"\
                    \n1 <span style='color: red;'>{day_sky_veto.iloc[id_v, 3].values[0]}</span> \
                    \n2 <span style='color: red;'>Точки инь и ян каналов в области живота (ниже диафрагмы)</span>"
            elif (day_iero[0]=='戊') or (day_iero[0]=='己'):
                str_veto = "<span style='color: red;'>Точки инь и ян каналов в области живота (ниже диафрагмы)</span>"
            elif (zya_zy==day_sky_veto.iloc[id_v, 1].values[0]) or (zya_zy==day_sky_veto.iloc[id_v, 2].values[0]):
                str_veto = f"<span style='color: red;'>{day_sky_veto.iloc[id_v, 3].values[0]}</span>"
            else:
                str_veto = "<span style='color: #3d7945;'>Запрета нет.</span>"
            
            veto = read_files('veto')
            sky_hands = read_files('sky_hands')
            earth_legs = read_files('earth_legs')
            str_result = f"<div><p>День: <span style='font-weight: bold;'>{in_yan_day.capitalize()}</span>\
                        \n<br>ЦзяЦзы дня: № <span style='font-weight: bold; color: #1e88e5;'>{zya_zy}</span>\
                        \n<br>Точки 24 Сезонов (Жэнь май): <span style='color: #1e88e5;'>{'  ||  '.join(season).strip()}</span>\
                        \n<br>День недели: <span style='font-weight: bold;'>{dow_dict[pd.to_datetime(our_date).day_of_week]}</span>\
                        \n<br>Планета-покровитель: <span style='color: #3d7945; font-weight: bold;'>{planet.capitalize()}</span>\
                        \n<br><span style='font-style: italic;'>Запрет по 4 сезонам:</span> <span style='font-weight: bold;'>{veto[veto['месяц']==month_iero[1]]['запрет'].values[0]}</span>\
                        \n<br><span style='font-style: italic;'>Запреты на ручные каналы:</span>\
                        \n  <br><span style='font-weight: bold; color: red;'>{sky_hands[sky_hands['Иероглиф']==day_iero[0]]['канал'].values[0]}</span>, \
                                <span style='font-weight: bold;'>{sky_hands[sky_hands['Иероглиф']==day_iero[0]]['сторона_тела'].values[0]} сторона:  пять точек транспортировки и точки между ними (до локтя)</span>\
                        \n<br><span style='font-style: italic;'>Запреты на ножные каналы:</span>\
                        \n  <br><span style='font-weight: bold; color: red;'>{earth_legs[earth_legs['Иероглиф']==month_iero[1]]['канал'].values[0]}</span>, \
                                <span style='font-weight: bold; '>{earth_legs[earth_legs['Иероглиф']==month_iero[1]]['сторона_тела'].values[0]} сторона: пять точек транспортировки и точки между ними (до колена)</span>\
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            our_date = data.get('our_date')
            our_date_lst = our_date.split("T")[0].split("-")
            our_date = datetime(int(our_date_lst[0]), int(our_date_lst[1]), int(our_date_lst[2])).date()
            day_iero = data.get('day_iero')
            CURRENT_TIME_SOLAR = data.get('current_time')
            method_index = int(data.get('methodIndex'))
            methods = [" ", "ЛУННЫЕ ДВОРЦЫ", "ФЭЙ ТЭН БА ФА", 
                      "ЛИН ГУЙ БА ФА", "ТАЙ ЯН БА ФА", 
                      "ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА"]
            selected_method = methods[method_index]
            
           
            def calculate_method(selected_method, our_date = our_date, day_iero=day_iero):
                method = selected_method
                feitenbafa = pd.read_csv("accounts/data/feitenbafa.csv")
                for_feitenbafa = pd.read_csv("accounts/data/for_feitenbafa.csv")

                day_predictions = feitenbafa.merge(for_feitenbafa.rename(columns={"Иероглиф":day_iero[0]}))
                feitenbafa_day = day_predictions[[day_iero[0], 'Иероглиф',	'Время',	'Канал',	'Точки']]

                current_hour = re.search(r"(\d*)", CURRENT_TIME_SOLAR)[0]

                # Определяем час по текущему времени.
                if (int(current_hour) == 23) or (int(current_hour) == 0):
                    current_hour_china_list = feitenbafa_day.iloc[0].values
                else:
                    for h in range(1,12):
                        if (int(current_hour) >= (feitenbafa['Время_int'][h])) & (int(current_hour) < (feitenbafa['Время_int'][h]+2)):
                            current_hour_china_list = feitenbafa_day.iloc[h].values
                            break

                current_hour_china = ''.join(current_hour_china_list[:2])
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
                        return f'<img src="data:image/png;base64,{image_base64(im)}">'

                    path_yan = 'accounts/data/images/yan.png'
                    path_in = 'accounts/data/images/in.png'

                    # Считаем лунную стоянку
                    for k, v in moon_palace.items():
                        if our_date.year in v:
                            first_step = k
                    if (our_date.year in vis_yaer) & (pd.to_datetime(our_date) > pd.to_datetime(f"{our_date.year}-02-28")):
                        first_step = first_step+1
                    lunar_day = first_step + sec_step[our_date.month]+ our_date.day

                    moon_palace_df = read_files('moon_palace_df')
                    while lunar_day > 28:
                        lunar_day+=-28
                    if lunar_day in range(1, 15):
                        lunar_day_ton = lunar_day+14
                    else:
                        lunar_day_ton = lunar_day-14
                    symbol = moon_palace_df[moon_palace_df["Лунный_день"]==lunar_day]["Иероглиф"].values[0]
                    val = moon_palace_df[moon_palace_df["Лунный_день"]==lunar_day]["Созвездие"].values[0]
                    point = moon_palace_df[moon_palace_df["Лунный_день"]==lunar_day][["Точка_Ду_май", "Название"]].values[0][0] + \
                        "||" + moon_palace_df[moon_palace_df["Лунный_день"]==lunar_day][["Точка_Ду_май", "Название"]].values[0][1]

                    df_img = pd.DataFrame({
                        'URL':[path_yan, path_in],
                    })
                    df_sed = pd.DataFrame({
                        'Помочь выйти событию (седирование)': [" ", " "],
                        'Точки':[man[lunar_day-1], woman[lunar_day-1]]    
                    })
                    df_ton = pd.DataFrame({
                        'Заставить выйти событие (тонизация)': [" ", " "],
                        'Точки':[man[lunar_day_ton-1], woman[lunar_day_ton-1]]    
                    })

                    try:
                        df_sed['Помочь выйти событию (седирование)'] = df_img.URL.map(lambda f: get_thumbnail(f))
                        df_sed = df_sed.to_html(formatters={'Помочь выйти событию (седирование)': image_formatter}, escape=False, header= False, index=False, border=0)
                    
                        df_ton['Заставить выйти событие (тонизация)'] = df_img.URL.map(lambda f: get_thumbnail(f))
                        df_ton = df_ton.to_html(formatters={'Заставить выйти событие (тонизация)': image_formatter}, escape=False, header= False, index=False, border=0)
                    except:
                        logger.error(f"Не получены данные для создания таблиц")
                    
                    return f" \
                        <div>\
                            <div>\
                                Лунная стоянка: <span style='font-weight: bold;'>{str(lunar_day)}</span> <span style='font-weight: bold; color: red;'>{symbol}</span> <span style='font-weight: bold;'>{val.capitalize()}</span> \
                                <br>Точки 28 Лунных Стоянок (Ду май): <span style='font-weight: bold;'>{point}</span> \
                                <br>\
                                <br><span style='font-style: italic;'>Техника 28 Лунных Стоянок</span>\
                                <br>Помочь выйти событию (седирование)\
                                <div class='table_moon_palace'>\
                                    <table>\
                                        {df_sed}\
                                    </table>\
                                </div>\
                                <br>Заставить выйти событие (тонизация)\
                                <div class='table_moon_palace'>\
                                    <table>\
                                        {df_ton}\
                                    </table>\
                                </div>\
                            </div>\
                        </div>\
                        "

                elif method=="ФЭЙ ТЭН БА ФА":                    
                    feitenbafa_day_disp = feitenbafa_day.iloc[:, 1:].T
                    feitenbafa_day_disp.to_csv("accounts/data/feitenbafa_day_disp.csv", index=False)
                    feitenbafa_day_disp = pd.read_csv("accounts/data/feitenbafa_day_disp.csv", header=1)

                    for c in feitenbafa_day_disp.columns:
                        feitenbafa_day_disp[c] = feitenbafa_day_disp[c].apply(highlight_words)
                    
                    styled_df_f = feitenbafa_day_disp.style.hide(
                        axis="index"
                        ).map(lambda x: f"background-color: {'yellow' if x else 'red'}", subset=current_hour_china[1]).to_html()

                    return f"\
                        {' || '.join(current_hour_china_list[1:])}\
                        <div>\
                            <table>\
                                {styled_df_f}\
                            </table>\
                        </div>\
                        "

                elif method=="ЛИН ГУЙ БА ФА":
                    for_lin_gui_ba_fa = pd.read_csv("accounts/data/for_lin_gui_ba_fa.csv")
                    
                    sky_hands = read_files('sky_hands')
                    earth_legs = read_files('earth_legs')
                    linguibafa = []
                    for i in feitenbafa_day.index:
                        summ = sky_hands[sky_hands['Иероглиф']==day_iero[0]]['i_day'].values[0] + \
                                    sky_hands[sky_hands['Иероглиф']==feitenbafa_day.iloc[i, 0]]['i_hour'].values[0] + \
                                    earth_legs[earth_legs['Иероглиф']==day_iero[1]]['j_day'].values[0] + \
                                    earth_legs[earth_legs['Иероглиф']==feitenbafa_day.iloc[i, 1]]['j_hour'].values[0]

                        cicle = read_files('cicle')
                        if cicle[cicle['Иероглиф']==day_iero]['инь_ян'].values[0] == 'ян':
                            res = summ%9
                            if res == 0:
                                res = 9
                        else:
                            res = summ%6
                            if res == 0:
                                res = 6  
                            
                        linguibafa_lst = list(feitenbafa_day.iloc[i,:3].values)
                        linguibafa_lst.extend(for_lin_gui_ba_fa[for_lin_gui_ba_fa['res']==res].values[0][1:])
                        linguibafa.append(linguibafa_lst)

                        
                    linguibafa_df = pd.DataFrame(
                        data=linguibafa,
                        columns=[feitenbafa_day.columns[0], feitenbafa_day.columns[1], feitenbafa_day.columns[2],"Канал", "Точка", "Название_точки"]
                    )

                    linguibafa_df[linguibafa_df.columns[1:]].T.to_csv("accounts/data/linguibafa_df_disp.csv", index=False)
                    linguibafa_df_disp = pd.read_csv("accounts/data/linguibafa_df_disp.csv", header=1)

                    for c in linguibafa_df_disp.columns:
                        linguibafa_df_disp[c] = linguibafa_df_disp[c].apply(highlight_words)
                    
                    df = linguibafa_df_disp.style.hide(axis="index")\
                            .map(lambda x: f"background-color: {'yellow' if x else 'red'}", subset=current_hour_china[1])\
                            .to_html()
                        
                    
                    linguibafa_current_hour = linguibafa_df[linguibafa_df['Иероглиф']==current_hour_china[1]]
                    
                    return f"\
                        {' || '.join(linguibafa_current_hour.iloc[0,1:].values.tolist())}\
                        <div>\
                            <table>\
                                {df}\
                            </table>\
                        </div>\
                        "
                elif method=="ТАЙ ЯН БА ФА":
                    list_tai = os.listdir("accounts/data/tai_yan_ba_fa/")
                    for l in list_tai:
                        if day_iero[0] in l:
                            file=re.findall(f'(\w*{day_iero[0]}\w*.csv)', l)

                    tai_yan_ba_fa = pd.read_csv(f"accounts/data/tai_yan_ba_fa/{file[0]}")

                    
                    for i in tai_yan_ba_fa.index:
                        for j in tai_yan_ba_fa.columns:
                            if i%2==0:
                                tai_yan_ba_fa.iloc[i, int(j)] = tai_yan_ba_fa.iloc[i, int(j)] + " " + tai_yan_ba_fa.iloc[i+1, int(j)]
                                
                    df = tai_yan_ba_fa.drop(tai_yan_ba_fa.index[range(1,42, 2)], axis=0).reset_index(drop=True)
                    df.iloc[:,0] = df.iloc[:,0].str.strip()
                    df.iloc[:,1] = df.iloc[:,1].str.strip()
                    
                    d = int(our_date.day)
                    m = int(our_date.month)
                    y = int(our_date.year)
                    h = int(CURRENT_TIME_SOLAR.split(":")[0])
                    mi = int(CURRENT_TIME_SOLAR.split(":")[1])

                    current_time_solar = datetime(y, m, d, h, mi).time()
                    
                    for i in df.index:
                        start_time = datetime(y, m, d, hour=int(df.iloc[i,1].split(" - ")[0].split(".")[0]), minute=int(df.iloc[i,1].split(" - ")[0].split(".")[1])).time()
                        end_time = datetime(y, m, d, hour=int(df.iloc[i,1].split(" - ")[1].split(".")[0]), minute=int(df.iloc[i,1].split(" - ")[1].split(".")[1])).time()
                        if (current_time_solar >= start_time) & (current_time_solar < end_time):
                            ser = " || ".join(df.iloc[i].to_list())
                            ind = i
                            break
                   
                    df_styled = df.style\
                        .hide(axis="index", level=0)\
                        .set_properties(**{'background-color': 'yellow'}, subset=ind).to_html()
                    
                   
                    return f"\
                        <div>На текущий час:</div>\
                        <div>{ser}</div>\
                        <div class='scrollable-table'>\
                            {df_styled}\
                        </div>\
                        "
               
                elif method=="ДА СЯО ЧЖОУ ТЯНЬ ЖЭНЬ ФА":
                    da_syao = pd.read_csv("accounts/data/da_syao.csv")
                    current_hour_china_list = da_syao[current_hour_china[1]].to_list()
                    current_hour_china_str = ' || '.join(current_hour_china_list)
                    for c in da_syao.columns:
                        da_syao[c] = da_syao[c].apply(highlight_words)

                    df = da_syao.style.hide(axis="index").map(lambda x: f"background-color: {'yellow' if x else 'red'}", subset=current_hour_china[1]).to_html()

                    return f"\
                        <div>{current_hour_china_str}</div>\
                        <table>\
                            {df}\
                        </table>\
                        "        
                
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


