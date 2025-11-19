from ...utils import highlight_words, read_files

current_channel_global = ""

def get_current_channel_lingui():
    """Функция для получения текущего current_channel"""
    global current_channel_global
    return current_channel_global

def get_lingui(feitenbafa, day_iero, current_hour_china, headOfT, timeOfT):
    global current_channel_global

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
            current_channel_global = linguibafa_row['0']
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