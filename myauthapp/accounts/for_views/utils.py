import json
from .constants import *
from datetime import date
from itertools import cycle
from django.conf import settings





def read_files(table_name):
    with open(f"{settings.BASE_DIR}/accounts/data/{table_name}.json", encoding='utf-8') as f: # Открываем файл и связываем его с объектом "f"
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