// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {

    // Глобальное состояние расчета
    window.calculationState = {
        birthdayData: null,
        cityData: null,
        ourDateData: null,
    };

    // Элементы UI
    const uiElements = {
        birthdayInput: document.getElementById('birthdayInput'),
        citySearch: document.getElementById('citySearch'),
        citySelect: document.getElementById('citySelect'),
        ourdateInput: document.getElementById('ourdateInput'),
        methodSelect: document.getElementById('methodSelect'),
        changeTimeCheckbox: document.getElementById('changeTime'),
        birthdayResult: document.getElementById('birthdayResult'),
        cityResult: document.getElementById('cityResult'),
        checkTime: document.getElementById('checkTime'),
        ourdateResult: document.getElementById('ourdateResult'),
        methodResult: document.getElementById('methodResult')
    };

    // Инициализация с передачей uiElements
    initCityAutocomplete(uiElements);
    setupEventListeners(uiElements);

});

// --- ИНИЦИАЛИЗАЦИЯ АВТОДОПОЛНЕНИЯ ГОРОДОВ (теперь принимает uiElements) ---
function initCityAutocomplete(uiElements) {
    let cities = [];
    
    // Загружаем города асинхронно
    fetch('/city-search/?q=')
        .then(response => response.json())
        .then(data => {
            cities = data;
            console.log('Города загружены:', cities.length);
        })
        .catch(error => console.error('Ошибка загрузки городов:', error));

    uiElements.citySearch?.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        uiElements.citySelect.innerHTML = '';
        
        if (searchTerm.length < 2) {
            uiElements.citySelect.style.display = 'none';
            return;
        }

        const filtered = cities.filter(city => 
            city.toLowerCase().includes(searchTerm)
        ).slice(0, 15);
        
        if (filtered.length > 0) {
            filtered.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                uiElements.citySelect.appendChild(option);
            });
            uiElements.citySelect.style.display = 'block';
        } else {
            uiElements.citySelect.style.display = 'none';
        }
    });
    
    // Обработчик выбора города из выпадающего списка
    uiElements.citySelect?.addEventListener('click', function(e) {
        if (e.target.tagName === 'OPTION') {
            uiElements.citySearch.value = e.target.value;
            uiElements.citySelect.style.display = 'none';
            // ГОРОД ВЫБРАН -> НЕМЕДЛЕННО ОТПРАВЛЯЕМ НА СЕРВЕР
            submitCityData(uiElements); // Теперь uiElements передается правильно
        }
    });
    
    // Скрытие списка при клике вне его области
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-container')) {
            uiElements.citySelect.style.display = 'none';
        }
    });
}

// --- НАСТРОЙКА ВСЕХ ОСНОВНЫХ ОБРАБОТЧИКОВ СОБЫТИЙ ---
function setupEventListeners(ui) {
    // 1. День рождения: Отправка по Enter
    ui.birthdayInput?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            processBirthdayData(ui);
        }
    });

    // 2. Город: Отправка по Enter (дублирует выбор из списка)
    ui.citySearch?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.trim()) {
            submitCityData(ui);
        }
    });

    // 3. Дата расчета: КОМБИНИРОВАННАЯ обработка
    setupDateInputHandling(ui);

    // 4. Метод: Отправка сразу при изменении
    ui.methodSelect?.addEventListener('change', function() {
        processMethodData(ui);
    });

    // 5. Чекбокс времени
    ui.changeTimeCheckbox?.addEventListener('change', function() {
        if (window.calculationState.cityData) {
            window.calculationState.cityData.current_time = this.checked 
                ? window.calculationState.cityData.admin_time 
                : window.calculationState.cityData.solar_time;

            updateCityUI(ui, window.calculationState.cityData);

            // Пересчитываем ВСЕ последующие этапы
            if (window.calculationState.ourDateData) {
                processOurDateData(ui).then(() => {
                    // После пересчета даты пересчитываем метод, если он выбран
                    if (ui.methodSelect.value !== " " && window.calculationState.ourDateData) {
                        processMethodData(ui);
                    }
                });
            }
        }
    });
}

// --- ФУНКЦИЯ ОБРАБОТКИ ДНЯ РОЖДЕНИЯ ---
async function processBirthdayData(ui) {
    const birthday = ui.birthdayInput.value;
    if (!birthday) return;

    try {
        const response = await fetch(window.processBirthdayUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.csrfToken },
            body: JSON.stringify({ birthday })
        });
        const data = await response.json();
        
        if (data.success) {
            window.calculationState.birthdayData = data;
            ui.birthdayResult.innerHTML = `<p>${data.birthday_table}</p>`;
            ui.citySearch.focus();
        } else {
            alert('Ошибка (ДР): ' + data.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке данных (ДР)');
    }
}

// --- ФУНКЦИЯ ОБРАБОТКИ ГОРОДА ---
async function submitCityData(ui) {
    const city = ui.citySearch.value;
    if (!city) return;

    try {
        const response = await fetch(window.processCityUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.csrfToken },
            body: JSON.stringify({ city })
        });
        const data = await response.json();
        
        if (data.success) {
            window.calculationState.cityData = data;
            updateCityUI(ui, data);
            ui.ourdateInput.disabled = false;
            ui.ourdateInput.focus();

            // АВТОМАТИЧЕСКИ ПЕРЕСЧИТЫВАЕМ ДАТУ И МЕТОД, ЕСЛИ ОНИ УЖЕ ВВЕДЕНЫ
            if (window.calculationState.ourDateData) {
                processOurDateData(ui).then(() => {
                    recalculateMethodIfNeeded(ui);
                });
            }

        } else {
            alert('Ошибка (Город): ' + data.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке данных (Город)');
    }
}

// --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОБНОВЛЕНИЯ UI ГОРОДА ---
function updateCityUI(ui, data) {
    const isAdminTime = ui.changeTimeCheckbox.checked;
    const currentTimeToUse = isAdminTime ? data.admin_time : data.solar_time;

    ui.cityResult.innerHTML = `
        <p><span class="rainbow-text">Текущее административное время:</span> 
        <span style="color: #4a7b9d; font-size: 16px; font-weight: bold;">${data.admin_time}</span></p>               
        <p><span class="rainbow-text">Текущее солнечное время:</span> 
        <span style="color: #4a7b9d; font-size: 16px; font-weight: bold;">${data.solar_time}</span></p>
        <p style="font-size: 12px">Рассчет по умолчанию выполняется по солнечному времени.
        <br>Если нужен рассчет по времени административному, поставьте галочку ниже:</p>
    `;
    ui.checkTime.innerHTML = `<div>Рассчетное время: <strong>${currentTimeToUse}</strong></div>`;

    data.current_time = currentTimeToUse;
}

// --- ФУНКЦИЯ ОБРАБОТКИ ДАТЫ РАСЧЕТА ---
async function processOurDateData(ui) {
    const ourdate = ui.ourdateInput.value;
    if (!ourdate || !window.calculationState.cityData) return;

    // Проверка на валидность даты
    if (!ourdate.match(/^\d{4}-\d{2}-\d{2}$/)) {
        console.log('Неверный формат даты');
        return;
    }

    const postData = {
        ourdate: ourdate,
        current_time: window.calculationState.cityData.current_time
    };

    try {
        // Показываем индикатор загрузки
        ui.ourdateResult.innerHTML = '<div class="loading">Загрузка...</div>';
        
        const response = await fetch(window.processOurDateUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.csrfToken },
            body: JSON.stringify(postData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.calculationState.ourDateData = data;
            ui.ourdateResult.innerHTML = `<p>${data.our_date_table}</p><p>${data.str_result}</p>`;
            
            // Автоматически пересчитываем метод, если он уже выбран
            recalculateMethodIfNeeded(ui);
            
        } else {
            ui.ourdateResult.innerHTML = `<div class="error">Ошибка: ${data.error}</div>`;
        }
    } catch (error) {
        console.error('Ошибка:', error);
        ui.ourdateResult.innerHTML = `<div class="error">Ошибка сети: ${error.message}</div>`;
    }
}


// --- УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ДЛЯ ОБРАБОТКИ ВВОДА ДАТЫ ---
function setupDateInputHandling(ui) {
    let dateInputTimeout = null;
    const DEBOUNCE_DELAY = 800; // Задержка для ручного ввода
    let lastProcessedValue = ''; // Для отслеживания уже обработанных значений

    // Функция для валидации даты
    function isValidDate(dateString) {
        const regex = /^\d{4}-\d{2}-\d{2}$/;
        if (!regex.test(dateString)) return false;
        
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    // Функция обработки даты (с проверкой на дублирование)
    function handleDateProcessing() {
        const currentValue = ui.ourdateInput.value;
        
        // Проверяем, что значение изменилось и оно валидно
        if (currentValue && currentValue !== lastProcessedValue && isValidDate(currentValue)) {
            lastProcessedValue = currentValue;
            processOurDateData(ui);
        }
    }

    // 1. Обработчик нажатия Enter
    ui.ourdateInput?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Предотвращаем стандартное поведение
            if (dateInputTimeout) {
                clearTimeout(dateInputTimeout); // Отменяем ожидающий таймаут
                dateInputTimeout = null;
            }
            handleDateProcessing();
        }
    });

    // 2. Обработчик изменения (для выбора из datepicker)
    ui.ourdateInput?.addEventListener('change', function() {
        if (dateInputTimeout) {
            clearTimeout(dateInputTimeout);
            dateInputTimeout = null;
        }
        handleDateProcessing();
    });

    // 3. Обработчик ввода с дебаунсингом (для ручного ввода без Enter)
    ui.ourdateInput?.addEventListener('input', function() {
        // Очищаем предыдущий таймаут
        if (dateInputTimeout) {
            clearTimeout(dateInputTimeout);
        }

        // Устанавливаем новый таймаут для обработки после паузы ввода
        dateInputTimeout = setTimeout(() => {
            handleDateProcessing();
            dateInputTimeout = null;
        }, DEBOUNCE_DELAY);
    });

    // 4. Обработчик потери фокуса (на случай, если пользователь ввел и перешел дальше)
    ui.ourdateInput?.addEventListener('blur', function() {
        if (dateInputTimeout) {
            clearTimeout(dateInputTimeout); // Отменяем таймаут, если он есть
            dateInputTimeout = null;
            handleDateProcessing(); // Немедленная обработка
        }
    });

    // 5. Дополнительно: обработка клика по календарной иконке (для некоторых браузеров)
    ui.ourdateInput?.addEventListener('click', function() {
        // Некоторые браузеры показывают календарь при клике на поле
        // Можно добавить дополнительную логику если нужно
    });
}


// --- ФУНКЦИЯ ОБРАБОТКИ МЕТОДА ---
async function processMethodData(ui) {
    const methodIndex = ui.methodSelect.value;
    if (methodIndex === " " || !window.calculationState.ourDateData || !window.calculationState.cityData) return;

    const postData = {
        methodIndex: methodIndex,
        our_date: window.calculationState.ourDateData.our_date_result,
        day_iero: window.calculationState.ourDateData.day_iero,
        current_time: window.calculationState.cityData.current_time
    };

    try {
        const response = await fetch(window.processMethodUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.csrfToken },
            body: JSON.stringify(postData)
        });
        const data = await response.json();
        
        if (data.success) {
            window.calculationState.methodData = data;
            ui.methodResult.innerHTML = `
                <div>
                    <h4>Метод: ${data.method}</h4>
                    <div>${data.result}</div>
                </div>
            `;
            ui.methodResult.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            ui.methodResult.innerHTML = `<div class="alert alert-danger">Ошибка: ${data.error}</div>`;
            ui.methodResult.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    } catch (error) {
        console.error('Ошибка:', error);
        ui.methodResult.innerHTML = `<div class="alert alert-danger">Ошибка сети: ${error.message}</div>`;
        ui.methodResult.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// --- ФУНКЦИЯ ДЛЯ ПЕРЕСЧЕТА МЕТОДА ПРИ ИЗМЕНЕНИИ ДАННЫХ ---
function recalculateMethodIfNeeded(ui) {
    // Если метод уже выбран и есть все необходимые данные - пересчитываем
    if (ui.methodSelect.value !== " " && 
        window.calculationState.ourDateData && 
        window.calculationState.cityData) {
        
        console.log('Автоматический пересчет метода из-за изменения данных...');
        processMethodData(ui);
    }
}