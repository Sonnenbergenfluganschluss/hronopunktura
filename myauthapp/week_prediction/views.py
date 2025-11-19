from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
from datetime import datetime, timedelta, date
from django.conf import settings
import csv


dolgoletie = {
    'ду-май':'жень-май',
    'чун-май':'дай-май',
    'чонг-май':'дай-май',
    'инь-цяо':'ян-цяо',
    'инь-вэй':'ян-вэй',
    'жень-май':'ду-май',
    'жэнь-май':'ду-май',
    'дай-май':'чонг-май',
    'ян-цяо':'инь-цяо',
    'ян-вэй':'инь-вэй',
}

skydoc = {
    'ду-май':'ян-цяо',
    'чун-май':'инь-вэй',
    'чонг-май':'инь-вэй',
    'инь-цяо':'жень-май',
    'ян-вэй':'дай-май',
    'ян-цяо':'ду-май',
    'инь-вэй':'чонг-май',
    'жень-май':'инь-цяо',
    'жэнь-май':'инь-цяо',
    'дай-май':'ян-вэй',
}

birthqi = {
    'ду-май':'инь-цяо',
    'чун-май':'ян-вэй',
    'чонг-май':'ян-вэй',
    'жень-май':'ян-цяо',
    'жэнь-май':'ян-цяо',
    'инь-вэй':'дай-май',
    'инь-цяо':'ду-май',
    'ян-вэй':'чонг-май',
    'ян-цяо':'жень-май',
    'дай-май':'инь-вэй',
}

def read_csv_files(table):       
    table_csv = pd.read_csv(f"{settings.BASE_DIR}/data/{table}.csv")
    return table_csv


def read_csv(table):
    lsts = []
    with open(f'{settings.BASE_DIR}/data/{table}.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            lsts.append(row)
    return lsts



################################################################################################

feitenbafa = read_csv_files('feitenbafa')
for_feitenbafa = read_csv_files('for_feitenbafa')
for_lin_gui_ba_fa = read_csv_files("for_lin_gui_ba_fa")
sky_hands = read_csv_files("sky_hands")
earth_legs = read_csv_files("earth_legs")

def week_prediction(request):
        context = {
            'title':'Расписание на неделю'
        }
        return render(request, 'week_prediction/week_prediction.html', context)



def predictions_process(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'})
    
    try:
        # Получаем данные от пользователя
        needed_channel = request.POST.get('needed_channel', 'Дай-май')
        needed_in_yan_day = request.POST.get('needed_in_yan_day', 'ян')
        needed_method = request.POST.get('needed_method', 'Небесный лекарь')
        needed_date = request.POST.get('needed_date', datetime.now().strftime("%d.%m.%Y"))
        needed_date = datetime.strptime(needed_date, "%Y-%m-%d").date()
        needed_methods = ["Продление жизни", "Небесный лекарь", "Порождающая ци"]
        
        # Валидация данных
        if not needed_date:
            return JsonResponse({'success': False, 'error': 'Date is required'})
        

        calendar = read_csv_files('calendar')
        calendar['date'] = pd.to_datetime(calendar['date'])

        # # needed_time = ['辰', '巳', '午', '未']

        needed_pair = []
        if needed_method == needed_methods[1]:
            needed_pair = [needed_channel, skydoc[needed_channel.lower()].capitalize()]
        elif needed_method == needed_methods[2]:
            needed_pair = [needed_channel, birthqi[needed_channel.lower()].capitalize()]
        else:
            needed_pair = [needed_channel, dolgoletie[needed_channel.lower()].capitalize()]

        week_predictions = {"our_date":[],
                            "day_iero":[],
                            "in_yan_day":[],}
        
        for n in range(7):
            our_date = needed_date + timedelta(days=n)
            if our_date:
                try:
                    d = int(our_date.day)
                    m = int(our_date.month)
                    y = int(our_date.year)
                    our_date = date(y, m, d)
                    week_predictions["our_date"].append(our_date)

                except:
                    print("Некорректная дата, попробуйте снова!")

        seasons = read_csv_files('seasons')
        cicle = read_csv_files('cicle')


        cols = ""
        feiten = ""
        lingui = ""
        taiyan = ""

        for our_date in week_predictions["our_date"]:
            cols += f"<th  style='font:14; padding:2px;'>{our_date.strftime('%d.%m.%Y')}</th>"
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
            day_iero = cicle[cicle["Название_calendar"] == day_o]["Иероглиф"].values[0]
            week_predictions["day_iero"].append(day_iero)
            in_yan_day = cicle[cicle['Название_calendar'] == day_o]['инь_ян'].values[0]
            week_predictions["in_yan_day"].append(in_yan_day)


    ######### ФЭЙ ТЭН БА ФА ##########
            day_predictions = feitenbafa.merge(for_feitenbafa.rename(columns={"Иероглиф":day_iero[0]}))
            feitenbafa_day = day_predictions[[day_iero[0], 'Иероглиф',	'Время',	'Канал',	'Точки']]
            
            fen_time = ""
            for row in feitenbafa_day.index:
                if (feitenbafa_day.loc[row, 'Канал'] == needed_channel):
                    dict_of_row = feitenbafa_day.iloc[row].to_dict()
                    fen_time += f"{dict_of_row['Время']}<br>"
            feiten += f"<td>{fen_time}</td>"

    ######### ЛИН ГУЙ БА ФА ##########
            

            
            linguibafa = ""
            for i in feitenbafa_day.index:
                summ = sky_hands[sky_hands['Иероглиф']==day_iero[0]]['i_day'].values[0] + \
                            sky_hands[sky_hands['Иероглиф']==feitenbafa_day.iloc[i, 0]]['i_hour'].values[0] + \
                            earth_legs[earth_legs['Иероглиф']==day_iero[1]]['j_day'].values[0] + \
                            earth_legs[earth_legs['Иероглиф']==feitenbafa_day.iloc[i, 1]]['j_hour'].values[0]

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
                if needed_channel in linguibafa_lst:
                    linguibafa += f"{linguibafa_lst[2]}<br>"
            lingui += f"<td>{linguibafa}</td>"
 

    ######### ТАЙ ЯН БА ФА ##########
            if in_yan_day == needed_in_yan_day:
                list_tai = ["丁壬", "丙辛", "乙庚", "戊癸", "甲己"]
        
                dict_tai = {"丁壬":"first",
                "丙辛":"second",
                "乙庚":"trid",
                "戊癸":"fourth",
                "甲己":"fiveth",}
                
                file = []
                for l in list_tai:
                    if day_iero[0] in l:
                        file.append(l)
                
                tai_yan_ba_fa = read_csv(f'tai_yan_ba_fa/{dict_tai[file[0]]}')
                rows = ""
                for row in tai_yan_ba_fa:
                    s_row = " ".join(row)
                    if needed_pair[0] in s_row:
                        if (needed_pair[1] in s_row):
                            if len(rows) == 0:
                                rows += f"{row[1]}<br>"
                            else:
                                endp = int(rows.rstrip("<br>").split(" - ")[-1].split(".")[0])
                                nextp = int(row[1].split(" - ")[0].split(".")[0])
                                if endp == nextp:
                                    rows = rows.replace(rows.rstrip("<br>").split(" - ")[-1], row[1].split(" - ")[1])
                                else:
                                    rows += f"{row[1]}<br>"

                taiyan += f"<td>{rows}</td>"
            else:
                taiyan += f"<td>-</td>"
            
##############################################################################################


            table = f'''<table>
                            <tr style="font:14; padding:2px;">
                                <th style="font:14; padding:2px;"> Метод </th>
                                {cols}
                            </tr>
                            <tr>
                                <td> Фей тен </td>
                                {feiten}
                            </tr>
                            <tr>
                                <td> Лин Гуй </td>
                                {lingui}
                            </tr>
                            <tr>
                                <td> Тай Ян <br>{needed_method} <br>{needed_pair[0]} - {needed_pair[1]}</td>
                                {taiyan}
                            </tr>
                                    
                        </table>'''


        result = {
            'success': True,
            'table_predictions': table,
            'user_input': {
                'channel': needed_channel,
                'in_yan': needed_in_yan_day,
                'method': needed_method,
                'date': needed_date
            }
        }
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e)
        }
    
    return JsonResponse(result)