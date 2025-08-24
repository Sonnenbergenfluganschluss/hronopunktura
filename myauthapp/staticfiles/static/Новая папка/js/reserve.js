document.addEventListener('DOMContentLoaded', function() {
    // Инициализация данных
    window.complexData = JSON.parse(sessionStorage.getItem('complexData')) || {};
    
    // Получаем URL и CSRF токен из data-атрибутов
    window.processBirthdayUrl = document.getElementById('birthday-form')?.dataset.url;
    window.processCityUrl = document.getElementById('city-form')?.dataset.url;
    window.processOurDateUrl = document.getElementById('ourdate-form')?.dataset.url;
    window.processMethodUrl = document.getElementById('method-form')?.dataset.url;
    window.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    // Загружаем города через отдельный endpoint или data-атрибут
    loadCities();
    
    // Инициализация обработчиков
    setupInputHandlersWithAutoFocus();
    restoreUIState();
});

async function loadCities() {
    try {
        const response = await fetch('/api/cities/'); // Создайте этот endpoint в Django
        if (response.ok) {
            window.citiesJson = await response.json();
            initCityAutocomplete();
        }
    } catch (error) {
        console.error('Failed to load cities:', error);
    }
}

function restoreUIState() {
    // Восстановление состояния элементов
    if (window.complexData.birthday) {
        document.getElementById('citySearch')?.focus();
    }
    if (window.complexData.current_time) {
        document.getElementById('ourdateInput')?.disabled = false;
    }
}