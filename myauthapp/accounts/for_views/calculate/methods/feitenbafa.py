from ...utils import highlight_words


def get_feiten(feitenbafa, current_hour_china, headOfT, timeOfT):
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