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