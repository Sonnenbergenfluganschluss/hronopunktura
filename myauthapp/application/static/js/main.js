
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