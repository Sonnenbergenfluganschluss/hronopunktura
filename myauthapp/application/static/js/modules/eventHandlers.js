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