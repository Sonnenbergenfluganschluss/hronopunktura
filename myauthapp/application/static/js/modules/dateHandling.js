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