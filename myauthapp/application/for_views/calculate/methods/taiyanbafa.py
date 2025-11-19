import csv
from datetime import datetime
from django.conf import settings
from ...constants import color_dict, dolgoletie, skydoc, birthqi
from ...utils import highlight_words
import pandas as pd

current_row_global = ""
current_channel_global = ""

def get_luo_taiyan(current_channel, needed_channel):
    if len(current_channel) > 0:
        try:
            df = pd.read_csv(f'{settings.BASE_DIR}/data/luo_taiyan.csv', index_col='Unnamed: 0')
            result = df.loc[current_channel.lower(), needed_channel.lower()]
            return f"<div class='container'>Связь {current_channel} с каналом {needed_channel} через Luo-точки: {result}</div>"
        except Exception as e:
            return f"<div class='container'>Ошибка при получении Luo-точек: {str(e)}</div>"
    return "<div class='container'>Нет данных для расчета Luo-точек</div>"


def get_current_row():
    """Функция для получения текущего current_row"""
    global current_row_global
    return current_row_global

def get_current_channel():
    """Функция для получения текущего current_channel"""
    global current_channel_global
    return current_channel_global

def get_tayan_pair(current_row):
        channels = []
        for ch in current_row.split(','):
            if len(ch)>5:
                channels.append(ch.strip().split()[0].lower().replace('цяо','цзяо'))
            else:
                break

        channel = channels[0]
        if len(channels) == 2:
            res_tayan = f'''На данный момент благоприятна только комбинация 
                        <br><span style='font-weight: bold;'>Продление лет: </span>
                        <span style='font-weight: bold;'>{channel.capitalize()} - {dolgoletie[channel].capitalize()}</span>'''
        else:
            if skydoc[channel] in channels:
                res_tayan = f'''Продление лет: <span style='font-weight: bold;'>{channel.capitalize()}</span> - <span style='font-weight: bold;'>{dolgoletie[channel].capitalize()}</span>
                            <br>Небесный лекарь: <span style='font-weight: bold;'>{channel.capitalize()}</span> - <span style='font-weight: bold;'>{skydoc[channel].capitalize()}</span>
                            <br>Порождающая ци: <span style='font-weight: bold;'>{channel.capitalize()}</span> - <span style='font-weight: bold;'>{birthqi[channel].capitalize()}</span>
                            '''
            else:
                
                res_tayan = f'''или
                            <br>Продление лет: <span style='font-weight: bold;'>{channel.capitalize()}</span> - <span style='font-weight: bold;'>{dolgoletie[channel].capitalize()}</span>
                            <br>или
                            <br>Продление лет: <span style='font-weight: bold;'>{channels[2].capitalize()}</span> - <span style='font-weight: bold;'>{dolgoletie[channels[2]].capitalize()}</span>
                            '''
        return "<p>Открытые комбинации каналов на текущий час:</p>" + res_tayan


def get_taiyan(our_date, day_iero, CURRENT_TIME_SOLAR, headOfT, timeOfT):
    global current_row_global
    global current_channel_global
    
    list_tai = ['丁壬', '丙辛', '乙庚', '戊癸', '甲己']
    file = []
    for l in list_tai:
        if day_iero[0] in l:
            file.append(l)
            

    tai_yan_ba_fa = []
    with open(f"{settings.BASE_DIR}/data/tai_yan_ba_fa/{file[0]}.csv", 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            tai_yan_ba_fa.append(row)

    
    d = int(our_date.day)
    m = int(our_date.month)
    y = int(our_date.year)
    h = int(CURRENT_TIME_SOLAR.split(":")[0])
    mi = int(CURRENT_TIME_SOLAR.split(":")[1])


    current_time_solar = datetime(y, m, d, h, mi).time()
    tai_yan_ba_fa = tai_yan_ba_fa[1:]
    row_tab = ""
    current_row = ""
    current_channel = ""
    for row in tai_yan_ba_fa:
        start_time = datetime(y, m, d, hour=int(row[1].split(" - ")[0].split(".")[0]), minute=int(row[1].split(" - ")[0].split(".")[1])).time()
        end_time = datetime(y, m, d, hour=int(row[1].split(" - ")[1].split(".")[0]), minute=int(row[1].split(" - ")[1].split(".")[1])).time()
        
        if (current_time_solar >= start_time) & (current_time_solar < end_time):
            style_column = " id='x-row' style='background-color: yellow;'"
            current_row = f"{row[2]}, {row[3]}, {row[4]}, {row[5]}"
            current_channel = current_row.split(',')[0].split()[0]
        else:
            style_column = ""
        
        current_row_global = current_row
        current_channel_global = current_channel
        row_tab += f'''
            <tr{style_column}>
                <td> <span style='color:{color_dict[row[0]]};font-weight: bold'>{row[0]}</span> </td>
                <td> {row[1]} </td>
                <td> {highlight_words(row[2])} </td>
                <td> {highlight_words(row[3])} </td>
                <td> {highlight_words(row[4])} </td>
                <td> {highlight_words(row[5])} </td>
            </tr>
        '''
        
    table = f'''
        <div class='container'>
            {get_tayan_pair(current_row)}
        </div>
        <div class=".scrollable-table;" style="height: 300px; overflow: auto;">
            <div style="margin: auto 10px;" >
                <table>
                    {row_tab}
                </table>
            </div>
        </div>
        '''

    return table