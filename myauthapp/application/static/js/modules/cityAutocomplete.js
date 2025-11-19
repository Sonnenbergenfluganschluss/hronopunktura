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