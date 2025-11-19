from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from ..utils import highlight_words, read_files


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