Если ваш хостинг не поддерживает **pandas**, но вам нужно обрабатывать табличные данные, можно перейти на работу с **чистым Python** и стандартными библиотеками (`json`, `csv`, `collections` и т. д.).  

### **1. Загрузка JSON вместо CSV**
Если вы уже перевели данные в `.json`, их можно загрузить так:  

```python
import json

with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)  # если JSON — это список словарей
```

Если JSON имеет структуру:  
```json
[
    {"column1": "value1", "column2": "value2"},
    {"column1": "value3", "column2": "value4"}
]
```
то `data` станет списком словарей.  

---

### **2. Основные операции с JSON вместо pandas**
#### **Аналог `df.head()` — просмотр первых N строк**
```python
first_n_rows = data[:5]  # первые 5 строк
```

#### **Аналог `df['column']` — получение значений колонки**
```python
column_values = [row['column_name'] for row in data]
```

#### **Аналог `df[df['column'] > value]` — фильтрация**
```python
filtered_data = [row for row in data if row['column_name'] > 100]
```

#### **Аналог `df.groupby()` — группировка**
```python
from collections import defaultdict

grouped = defaultdict(list)
for row in data:
    key = row['group_column']
    grouped[key].append(row)

# Пример: среднее по группе
averages = {key: sum(item['value'] for item in group) / len(group) 
            for key, group in grouped.items()}
```

#### **Аналог `df.to_csv()` — сохранение в CSV**
```python
import csv

with open('output.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
```

---

### **3. Если нужно читать CSV без pandas**
Если JSON неудобен, можно работать с CSV напрямую:  
```python
import csv

with open('data.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)  # каждая строка — словарь
    data = list(reader)  # преобразуем в список словарей
```

---

### **4. Пример: обработка данных без pandas**
Допустим, у нас есть таблица **sales.json**:
```json
[
    {"product": "A", "price": 100, "quantity": 5},
    {"product": "B", "price": 200, "quantity": 3},
    {"product": "A", "price": 100, "quantity": 2}
]
```
**Задача:** посчитать общую выручку по каждому товару.  

**Решение:**
```python
import json
from collections import defaultdict

with open('sales.json', 'r') as file:
    sales = json.load(file)

revenue = defaultdict(int)
for item in sales:
    product = item['product']
    revenue[product] += item['price'] * item['quantity']

print(revenue)  # {'A': 700, 'B': 600}
```

---

### **Вывод**
- Если данные уже в **JSON**, работайте с ними через `json.load()` и стандартные структуры Python (списки, словари).  
- Если нужны **CSV**, используйте модуль `csv`.  
- Для сложных операций (группировка, агрегация) применяйте `collections.defaultdict`.  
- Такой подход не требует **pandas** и работает на любом хостинге.  

Если у вас есть конкретный пример кода на pandas, который нужно переписать — приведите его, и я помогу адаптировать.