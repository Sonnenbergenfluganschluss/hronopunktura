// Добавьте этот код в ваш шаблон или отдельный JS файл
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorContainer = document.getElementById('errorContainer');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = submitBtn.querySelector('.spinner-border');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Показываем спиннер
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;
        
        // Скрываем предыдущие ошибки
        errorContainer.classList.add('d-none');
        
        // Собираем данные формы
        const formData = new FormData(form);
        
        // Отправляем AJAX запрос
        fetch('predictions-process/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resultsContainer.innerHTML = data.table_predictions;
            } else {
                showError(data.error || 'Произошла ошибка при обработке запроса');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Ошибка сети или сервера');
        })
        .finally(() => {
            // Скрываем спиннер
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        });
    });
    
    // function showError(message) {
    //     errorContainer.textContent = message;
    //     errorContainer.classList.remove('d-none');
    //     resultsContainer.innerHTML = '';
    // }
    
    // // Устанавливаем сегодняшнюю дату по умолчанию, если не установлена
    // const dateInput = document.getElementById('needed_date');
    // if (!dateInput.value) {
    //     const today = new Date();
    //     dateInput.value = today.toISOString().split('T')[0];
    // }
});