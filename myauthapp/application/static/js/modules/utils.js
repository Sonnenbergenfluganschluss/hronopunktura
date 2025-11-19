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