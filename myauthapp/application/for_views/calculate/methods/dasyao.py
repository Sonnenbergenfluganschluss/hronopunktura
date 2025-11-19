from ...utils import highlight_words, read_files


def get_dasyao(current_hour_china, headOfT, timeOfT):
    da_syao = read_files("da_syao")
    
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