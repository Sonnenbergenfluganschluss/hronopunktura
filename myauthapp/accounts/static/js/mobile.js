// static/js/mobile.js
console.log('Mobile version loaded for Android');

// Детектирование проблемных браузеров
const userAgent = navigator.userAgent.toLowerCase();
const isProblematicBrowser = 
    userAgent.includes('chrome') || 
    userAgent.includes('yandex') || 
    userAgent.includes('yaBrowser');

console.log('Browser detection:', {
    userAgent: navigator.userAgent,
    isProblematicBrowser: isProblematicBrowser,
    isChrome: userAgent.includes('chrome'),
    isYandex: userAgent.includes('yandex') || userAgent.includes('yabrowser')
});

if (isProblematicBrowser) {
    console.log('Problematic browser detected - applying fixes');
    applyChromeYandexFixes();
}

function applyChromeYandexFixes() {
    // Исправления для проблемных браузеров
    document.documentElement.classList.add('chrome-yandex-fix');
    
    // Полифиллы для возможных отсутствующих функций
    if (typeof NodeList.prototype.forEach !== 'function') {
        NodeList.prototype.forEach = Array.prototype.forEach;
    }
}

// Глобальное состояние
window.calculationState = {
    birthdayData: null,
    cityData: null,
    ourDateData: null
};

// Основная инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mobile DOM loaded');
    
    // Проверяем все необходимые элементы
    const elements = {
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
    
    // Проверяем что все элементы найдены
    for (const [key, element] of Object.entries(elements)) {
        if (!element) {
            console.error('Missing element:', key);
            showError('Ошибка загрузки страницы');
            return;
        }
    }
    
    // Инициализируем приложение
    initMobileApp(elements);
});

function initMobileApp(ui) {
    console.log('Initializing mobile app for problematic browser');
    
    // Задержка для полной загрузки DOM
    setTimeout(() => {
        // 1. Инициализация автодополнения городов
        initMobileCitySearch(ui);
        
        // 2. Настройка обработчиков дат
        setupMobileDateHandling(ui);
        
        // 3. Настройка выбора метода
        setupMethodHandling(ui);
        
        // 4. Настройка чекбокса времени
        setupTimeCheckbox(ui);
        
        // 5. Специальные обработчики для проблемных браузеров
        if (isProblematicBrowser) {
            setupChromeYandexSpecificHandlers(ui);
        }
        
        console.log('Mobile app initialized successfully');
    }, 100);
}

function setupChromeYandexSpecificHandlers(ui) {
    // Предотвращение двойного клика
    let lastClickTime = 0;
    const preventDoubleClick = (element, handler) => {
        element.addEventListener('click', function(e) {
            const now = Date.now();
            if (now - lastClickTime < 500) {
                e.preventDefault();
                e.stopPropagation();
                return;
            }
            lastClickTime = now;
            handler.call(this, e);
        });
    };
    
    // Применяем ко всем кликабельным элементам
    const clickableElements = [
        ui.citySelect, 
        ...document.querySelectorAll('.city-option, .btn, button')
    ];
    
    clickableElements.forEach(el => {
        if (el) {
            el.style.cursor = 'pointer';
            preventDoubleClick(el, function() {});
        }
    });
}

// ==================== РАБОТА С ГОРОДАМИ ====================
function initMobileCitySearch(ui) {
    console.log('Setting up mobile city search');
    
    let cities = [];
    
    // Загружаем города
    fetch('/city-search/?q=')
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            cities = data;
            console.log('Cities loaded:', cities.length);
            setupCityEventHandlers(ui, cities);
        })
        .catch(error => {
            console.error('Failed to load cities:', error);
            showError('Не удалось загрузить города');
        });
}

function setupCityEventHandlers(ui, cities) {
    const search = ui.citySearch;
    const dropdown = ui.citySelect;
    
    // Обработчик ввода
    search.addEventListener('input', function() {
        const term = this.value.toLowerCase().trim();
        if (term.length === 0) {
            dropdown.style.display = 'none';
            return;
        }
        
        showCitySuggestions(term, cities, dropdown);
    });
    
    // Обработчик выбора города
    dropdown.addEventListener('click', function(e) {
        if (e.target.classList.contains('city-option')) {
            search.value = e.target.textContent;
            dropdown.style.display = 'none';
            processCitySelection(ui, search.value);
        }
    });
    
    // Обработчик отправки по кнопке "Готово" на клавиатуре
    search.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            dropdown.style.display = 'none';
            processCitySelection(ui, this.value);
        }
    });
    
    // Закрытие dropdown при клике вне его
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-container')) {
            dropdown.style.display = 'none';
        }
    });
}

function showCitySuggestions(term, cities, dropdown) {
    dropdown.innerHTML = '';
    
    const filtered = cities.filter(city => 
        city.toLowerCase().includes(term)
    ).slice(0, 8);
    
    if (filtered.length === 0) {
        const div = document.createElement('div');
        div.className = 'city-option';
        div.textContent = 'Город не найден';
        div.style.pointerEvents = 'none';
        dropdown.appendChild(div);
    } else {
        filtered.forEach(city => {
            const div = document.createElement('div');
            div.className = 'city-option';
            div.textContent = city;
            
            // Стили для проблемных браузеров
            if (isProblematicBrowser) {
                div.style.minHeight = '44px';
                div.style.display = 'flex';
                div.style.alignItems = 'center';
                div.style.padding = '12px 15px';
            }
            
            dropdown.appendChild(div);
        });
    }
    
    dropdown.style.display = 'block';
    
    // Для проблемных браузеров добавляем дополнительный z-index
    if (isProblematicBrowser) {
        dropdown.style.zIndex = '10000';
        dropdown.style.position = 'relative';
    }
}

async function processCitySelection(ui, city) {
    if (!city.trim()) {
        showError('Введите название города');
        return;
    }
    
    try {
        ui.cityResult.innerHTML = '<div class="mobile-loading">Определяем время...</div>';
        
        const response = await fetch(window.processCityUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ city: city.trim() })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.calculationState.cityData = data;
            updateMobileCityUI(ui, data);
            ui.ourdateInput.disabled = false;
            ui.ourdateInput.focus();
        } else {
            throw new Error(data.error || 'Ошибка сервера');
        }
        
    } catch (error) {
        console.error('City error:', error);
        ui.cityResult.innerHTML = `
            <div class="mobile-error">
                Ошибка: ${error.message}
            </div>
        `;
    }
}

function updateMobileCityUI(ui, data) {
    const isAdminTime = ui.changeTimeCheckbox.checked;
    const displayTime = isAdminTime ? data.admin_time : data.solar_time;
    
    ui.cityResult.innerHTML = `
        <div class="mobile-time-result">
            <div>Административное: <strong>${data.admin_time}</strong></div>
            <div>Солнечное: <strong>${data.solar_time}</strong></div>
            <div class="mobile-time-active">Используется: <strong>${displayTime}</strong></div>
        </div>
    `;
    
    data.current_time = displayTime;
}

// ==================== РАБОТА С ДАТАМИ ====================
function setupMobileDateHandling(ui) {
    const dateInput = ui.ourdateInput;
    
    // Для проблемных браузеров используем альтернативный подход
    if (isProblematicBrowser) {
        // Создаем кнопку для открытия datepicker
        const dateButton = document.createElement('button');
        dateButton.type = 'button';
        dateButton.textContent = 'Выбрать дату';
        dateButton.className = 'mobile-date-button';
        dateButton.style.marginTop = '10px';
        
        dateButton.addEventListener('click', function() {
            dateInput.focus();
            dateInput.click(); // Принудительно открываем datepicker
        });
        
        dateInput.parentElement.appendChild(dateButton);
        
        // Скрываем оригинальное поле, но оставляем функциональным
        dateInput.style.position = 'absolute';
        dateInput.style.opacity = '0';
        dateInput.style.width = '0';
        dateInput.style.height = '0';
    } else {
        // Для обычных браузеров добавляем кнопку "Применить"
        addMobileDateButton(ui);
    }
    
    // Основной обработчик
    dateInput.addEventListener('change', function() {
        if (this.value) {
            processMobileDate(ui, this.value);
        }
    });
    
    // Дополнительно - обработка потери фокуса
    dateInput.addEventListener('blur', function() {
        if (this.value) {
            processMobileDate(ui, this.value);
        }
    });
}

function addMobileDateButton(ui) {
    const wrapper = ui.ourdateInput.parentElement;
    const button = document.createElement('button');
    
    button.type = 'button';
    button.textContent = 'Применить';
    button.className = 'mobile-date-button';
    button.onclick = function() {
        if (ui.ourdateInput.value) {
            processMobileDate(ui, ui.ourdateInput.value);
        }
    };
    
    wrapper.appendChild(button);
}

async function processMobileDate(ui, dateString) {
    // Проверяем город
    if (!window.calculationState.cityData) {
        showError('Сначала выберите город');
        ui.citySearch.focus();
        return;
    }
    
    // Проверяем формат даты
    if (!isValidMobileDate(dateString)) {
        showError('Используйте формат ГГГГ-ММ-ДД');
        return;
    }
    
    try {
        ui.ourdateResult.innerHTML = '<div class="mobile-loading">Рассчитываем...</div>';
        
        const postData = {
            ourdate: dateString,
            current_time: window.calculationState.cityData.current_time
        };
        
        const response = await fetch(window.processOurDateUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify(postData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.calculationState.ourDateData = data;
            displayMobileDateResults(ui, data);
            ui.methodSelect.focus();
        } else {
            throw new Error(data.error || 'Ошибка расчета');
        }
        
    } catch (error) {
        console.error('Date error:', error);
        ui.ourdateResult.innerHTML = `
            <div class="mobile-error">
                Ошибка даты: ${error.message}
            </div>
        `;
    }
}

function isValidMobileDate(dateString) {
    return /^\d{4}-\d{2}-\d{2}$/.test(dateString);
}

function displayMobileDateResults(ui, data) {
    ui.ourdateResult.innerHTML = `
        <div class="mobile-date-result">
            <div class="mobile-date-table">${data.our_date_table}</div>
            <div class="mobile-date-info">${data.str_result}</div>
        </div>
    `;
}

// ==================== ВЫБОР МЕТОДА ====================
function setupMethodHandling(ui) {
    ui.methodSelect.addEventListener('change', function() {
        if (this.value !== " " && window.calculationState.ourDateData) {
            processMobileMethod(ui, this.value);
        }
    });
}

async function processMobileMethod(ui, methodIndex) {
    try {
        ui.methodResult.innerHTML = '<div class="mobile-loading">Применяем метод...</div>';
        
        const postData = {
            methodIndex: methodIndex,
            our_date: window.calculationState.ourDateData.our_date_result,
            day_iero: window.calculationState.ourDateData.day_iero,
            current_time: window.calculationState.cityData.current_time
        };
        
        const response = await fetch(window.processMethodUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify(postData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayMobileMethodResult(ui, data);
        } else {
            throw new Error(data.error || 'Ошибка метода');
        }
        
    } catch (error) {
        console.error('Method error:', error);
        ui.methodResult.innerHTML = `
            <div class="mobile-error">
                Ошибка метода: ${error.message}
            </div>
        `;
    }
}

function displayMobileMethodResult(ui, data) {
    ui.methodResult.innerHTML = `
        <div class="mobile-method-result">
            <h4>${data.method}</h4>
            <div>${data.result}</div>
        </div>
    `;
    
    // Плавная прокрутка к результату
    setTimeout(() => {
        ui.methodResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
function setupTimeCheckbox(ui) {
    ui.changeTimeCheckbox.addEventListener('change', function() {
        if (window.calculationState.cityData) {
            window.calculationState.cityData.current_time = this.checked 
                ? window.calculationState.cityData.admin_time 
                : window.calculationState.cityData.solar_time;
            
            updateMobileCityUI(ui, window.calculationState.cityData);
            
            // Пересчитываем дату если она уже была введена
            if (window.calculationState.ourDateData && ui.ourdateInput.value) {
                processMobileDate(ui, ui.ourdateInput.value);
            }
        }
    });
}

function showError(message) {
    // Простая функция показа ошибок
    alert('Ошибка: ' + message);
}

// Глобальные обработчики ошибок
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
});