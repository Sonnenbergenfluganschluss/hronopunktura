import base64
from datetime import datetime
from PIL import Image
from io import BytesIO
from django.conf import settings

from ...utils import read_files
from ...constants import man, woman, sec_step, moon_palace


def get_moon_palace(our_date, vis_yaer):
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

    path_yan = f'{settings.BASE_DIR}/accounts/data/images/yan.jpg'
    path_in = f'{settings.BASE_DIR}/accounts/data/images/in.jpg'

    for k, v in moon_palace.items():
        if our_date.year in v:
            first_step = k
    if (our_date.year in vis_yaer) & (our_date >= datetime.strptime(f"{our_date.year}-03-01", "%Y-%m-%d").date()):
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