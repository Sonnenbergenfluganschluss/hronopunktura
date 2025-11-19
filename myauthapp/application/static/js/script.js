
document.addEventListener('DOMContentLoaded', function() {
    // Глобальное состояние расчета
    window.calculationState = {
        birthdayData: null,
        cityData: null,
        ourDateData: null,
        needed_channel: null,
    };
    // Инициализация элементов UI
    const uiElements = initUIElements();
    
    // Инициализация всех модулей
    initCityAutocomplete(uiElements);
    setupEventListeners(uiElements);
});

function initUIElements() {
    return {
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
        methodResult: document.getElementById('methodResult'),
        neededChannel: document.getElementById('predictionForm'),
        luoTaiyanResult: document.getElementById('luoTaiyanResult'),
    };
}

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

    setupCitySearch(uiElements, cities);
    setupCitySelect(uiElements);
    setupCityDropdownClose(uiElements);
}

function setupCitySearch(uiElements, cities) {
    if (!uiElements.citySearch) return;
    
    uiElements.citySearch.addEventListener('input', function() {
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
}

    // Обработчик выбора города из выпадающего списка
function setupCitySelect(uiElements) {
    if (!uiElements.citySelect) return;
    
    uiElements.citySelect.addEventListener('click', function(e) {
        if (e.target.tagName === 'OPTION') {
            uiElements.citySearch.value = e.target.value;
            uiElements.citySelect.style.display = 'none';
                // ГОРОД ВЫБРАН -> НЕМЕДЛЕННО ОТПРАВЛЯЕМ НА СЕРВЕР
            submitCityData(uiElements);
        }
    });
}

// Скрытие списка при клике вне его области
function setupCityDropdownClose(uiElements) {
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-container')) {
            uiElements.citySelect.style.display = 'none';
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
            clearTimeout(dateInputTimeout);
            dateInputTimeout = null;
            handleDateProcessing();
        }
    });
}

function setupEventListeners(ui) {
    setupBirthdayHandlers(ui);
    setupCityHandlers(ui);
    setupDateHandlers(ui);
    setupMethodHandlers(ui);
    setupTimeCheckboxHandler(ui);
}

function setupBirthdayHandlers(ui) {
    if (ui.birthdayInput) {
        ui.birthdayInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processBirthdayData(ui);
            }
        });
    }
}

function setupCityHandlers(ui) {
    if (ui.citySearch) {
        ui.citySearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.value.trim()) {
                submitCityData(ui);
            }
        });
    }
}

function setupDateHandlers(ui) {
    setupDateInputHandling(ui);
}

function setupMethodHandlers(ui) {
    if (ui.methodSelect) {
        ui.methodSelect.addEventListener('change', function() {
            processMethodData(ui);
        });
    }
}


// function handleTimeChange(ui) {
//         if (ui.changeTimeCheckbox) {
//                 ui.changeTimeCheckbox.addEventListener('change', function() {
//                         if (window.calculationState && window.calculationState.cityData) {
//                                 window.calculationState.cityData.current_time = this.checked 
//                                     ? window.calculationState.cityData.admin_time 
//                     : window.calculationState.cityData.solar_time;

//                 updateCityUI(ui, window.calculationState.cityData);

//                 if (window.calculationState.ourDateData) {
//                     processOurDateData(ui).then(() => {
//                             if (ui.methodSelect && ui.methodSelect.value !== " ") {
//                             processMethodData(ui);
//                         }
//                     });
//                 }
//             }
//         });
//     }
// }  


function setupTimeCheckboxHandler(ui) {
    if (ui.changeTimeCheckbox) {
        ui.changeTimeCheckbox.addEventListener('change', function() {
            handleTimeChange(ui);
        });
    }
}

function handleTimeChange(ui) {
    if (window.calculationState && window.calculationState.cityData) {
        window.calculationState.cityData.current_time = ui.changeTimeCheckbox.checked 
        ? window.calculationState.cityData.admin_time 
        : window.calculationState.cityData.solar_time;

        updateCityUI(ui, window.calculationState.cityData);

        if (window.calculationState.ourDateData) {
            processOurDateData(ui).then(() => {
                if (ui.methodSelect && ui.methodSelect.value !== " ") {
                    processMethodData(ui);
                }
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    const luoTaiyanResult = document.getElementById('luoTaiyanResult');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const needed_сhannel = document.getElementById('needed_channel').value;
            
            if (!needed_сhannel) {
                luoTaiyanResult.innerHTML = '<div class="alert alert-warning">Пожалуйста, выберите канал</div>';
                return;
            }
            
            // Показываем индикатор загрузки
            luoTaiyanResult.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>';
            
            // Отправляем AJAX запрос
            fetch('/process-luo-taiyan/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({
                    needed_channel: needed_сhannel
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    luoTaiyanResult.innerHTML = data.result;
                } else {
                    luoTaiyanResult.innerHTML = `<div class="alert alert-danger">Ошибка: ${data.error}</div>`;
                }
            })
            .catch(error => {
                luoTaiyanResult.innerHTML = `<div class="alert alert-danger">Ошибка сети: ${error}</div>`;
            });
        });
    }
});

// static/js/modules/utils.js
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

function recalculateMethodIfNeeded(ui) {
    if (ui.methodSelect.value !== " " && 
        window.calculationState.ourDateData && 
        window.calculationState.cityData) {
        
        console.log('Автоматический пересчет метода из-за изменения данных...');
        processMethodData(ui);
    }
}