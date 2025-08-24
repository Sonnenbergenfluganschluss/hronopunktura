// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // ... (инициализация complexData и других переменных)
    window.complexData = {};
    const savedData = sessionStorage.getItem('complexData');
    if (savedData) {
        window.complexData = JSON.parse(savedData);
    }
    // Инициализация автодополнения городов
    initCityAutocomplete();

    // Настройка обработчиков с автоматическим фокусом
    setupInputHandlersWithAutoFocus();
});

function setupInputHandlersWithAutoFocus() {
    // 1. Обработчик для даты рождения
    const birthdayInput = document.getElementById('birthdayInput');
    birthdayInput?.addEventListener('keypress', async function(e) {
        if (e.key === 'Enter') {
            await processBirthday();
            if (window.complexData.birthday) {
                document.getElementById('citySearch').focus();
            }
        }
    });

    // 2. Обработчик для города (только по Enter)
    const citySearch = document.getElementById('citySearch');
    citySearch?.addEventListener('keypress', async function(e) {
        if (e.key === 'Enter' && this.value) {
            await submitCityHandler();
            if (window.complexData.current_time) {
                document.getElementById('ourdateInput').focus();
            }
        }
    });

    // 3. Обработчик для интересующей даты
    const ourdateInput = document.getElementById('ourdateInput');
    ourdateInput?.addEventListener('keypress', async function(e) {
        if (e.key === 'Enter') {
            await processOurdate();
            if (window.complexData.our_date) {
                document.getElementById('methodSelect').focus();
            }
        }
    });

    // 4. Обработчик для метода расчета (автоотправка)
    const methodSelect = document.getElementById('methodSelect');
    methodSelect?.addEventListener('keypress', async function(e) {
        if (e.key === 'Enter') {
            await submitMethodHandler();
            if (window.complexData.our_date) {
                document.getElementById('compiled').focus();
            }
        }
    }); 
}

// Функция обработки даты рождения
async function processBirthday() {
    const birthday = document.getElementById('birthdayInput').value;
    
    if (!birthday) return;
    
    try {
        const response = await fetch(window.processBirthdayUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ birthday })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('birthdayResult').innerHTML = `<p>${data.birthday_table}</p>`;
            window.complexData = {birthday: data.birthday_result};
        } else {
            alert('Ошибка: ' + data.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке данных');
    }
}

function initCityAutocomplete() {
    const cities = JSON.parse(window.citiesJson);
    console.log('Загружено городов:', cities.length);
    const searchInput = document.getElementById('citySearch');
    const citySelect = document.getElementById('citySelect');
    let selectedCity = null;
    
    searchInput?.addEventListener('input', function() {
        console.log('Ввод:', this.value);
        const searchTerm = this.value.toLowerCase();
        citySelect.innerHTML = '';
        
        const filtered = cities.filter(city => 
            city.toLowerCase().includes(searchTerm)
        ).slice(0, 15);
        
        if (filtered.length > 0) {
            filtered.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);
            });
            citySelect.style.display = 'block';
            document.getElementById('submitCity').disabled = false;
        } else {
            citySelect.style.display = 'none';
            document.getElementById('submitCity').disabled = true;
        }
    });
    
    citySelect?.addEventListener('click', function() {
        if (this.selectedIndex >= 0) {
            searchInput.value = this.options[this.selectedIndex].value;
            selectedCity = searchInput.value;
            this.style.display = 'none';
        }
    });
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-container')) {
            citySelect.style.display = 'none';
        }
    });
}

async function submitCityHandler() {
    const city = document.getElementById('citySearch').value;
    
    if (!city) {
        alert('Пожалуйста, выберите город из списка');
        return;
    }
    
    const postData = { 
        city,
        ...window.complexData
    };
    
    const response = await fetch(window.processCityUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify(postData)
    });
    
    const data = await response.json();
    
    if (data.success) {
        document.getElementById('cityResult').innerHTML = `
        <p>
        <span class="rainbow-text">Текущее административное время:</span> 
        <span style= "color: #4a7b9d; font-size: 16px; font-weight: bold;">${data.admin_time}</span>
        </p>               
        <p>
        <span class="rainbow-text">Текущее солнечное время:</span> 
        <span style= "color: #4a7b9d; font-size: 16px; font-weight: bold;">${data.solar_time}</span>
        </p>
        <p style="font-size: 12px">Рассчет по умолчанию выполняется по солнечному времени.
        <br>Если нужен рассчет по времени административному, поставьте галочкуниже:</p>
        `;
        
        if (complexData) {
            window.complexData.current_time = data.solar_time;
        }
        else {
            window.complexData = {'current_time':data.solar_time}
        }
        console.log('window.complexData: ', window.complexData);
        document.getElementById('checkTime').innerHTML = `<div>Рассчетное время ${window.complexData.current_time}</div>`;
        
        // Обработчик изменения чекбокса
        document.getElementById('changeTime').addEventListener('change', function() {
            window.complexData.current_time = this.checked ? data.admin_time : data.solar_time;
            console.log('Текущее время:', window.complexData.current_time); // Для отладки
            document.getElementById('checkTime').innerHTML = `<div>Рассчетное время ${window.complexData.current_time}</div>`;
        });
        console.log('window.complexData: ', window.complexData);


        document.getElementById('ourdateInput').disabled = false;
    } else {
        alert('Ошибка: ' + data.error);
    }
}


function ourDateKeypressHandler(e) {
    if (e.key === 'Enter') {
        processOurdate();
    }
}

async function processOurdate() {
    const ourdate = document.getElementById('ourdateInput').value;
    
    if (!window.complexData) {
        alert('window.complexData пуст');
        return;
    }
    
    const postData = {
        ourdate: ourdate,
        current_time: window.complexData.current_time
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
        document.getElementById('ourdateResult').innerHTML = `
        <p>${data.our_date_table}</p>
        <p>${data.str_result}</p>`;
        
        window.complexData.day_iero = data.day_iero;
        window.complexData.our_date = data.our_date_result;
        console.log('window.complexData: ', window.complexData);
    } else {
        alert('Ошибка: ' + data.error);
    }
}

async function submitMethodHandler() {
    const methodIndex = document.getElementById('methodSelect').value;

    if (!window.complexData) {
        alert('window.complexData пуст');
        return;
    }

    const postData = {
        methodIndex: methodIndex,
        ...window.complexData,
    };
    console.log('postData: ', postData);
    
    try {
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
            document.getElementById('methodResult').innerHTML = `
                <div class="alert alert-success">
                    <h4>Метод: ${data.method}</h4>
                    <div>${data.result}</div>
                </div>
            `;
        } else {
            document.getElementById('methodResult').innerHTML = `
                <div class="alert alert-danger">
                    Ошибка: ${data.error}
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('methodResult').innerHTML = `
            <div class="alert alert-danger">
                Ошибка сети: ${error.message}
            </div>
        `;
    }
}

// Сохранение данных при перезагрузке страницы
window.addEventListener('beforeunload', function() {
    sessionStorage.setItem('complexData', JSON.stringify(window.complexData));
});