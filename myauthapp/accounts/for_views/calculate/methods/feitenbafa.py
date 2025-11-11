from ...utils import highlight_words

current_channel_global = ""


def get_current_channel_feiten():
    """Функция для получения текущего current_channel"""
    global current_channel_global
    return current_channel_global


def get_feiten(feitenbafa, current_hour_china, headOfT, timeOfT):
    global current_channel_global
    channelOfT = ""
    pointsOfT = ""
    for row in feitenbafa:
        if row["Иероглиф_ЗВ"] == current_hour_china[0]:
            current_channel_global = row['Канал']
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