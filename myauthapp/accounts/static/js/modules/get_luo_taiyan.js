// Добавьте этот код в ваш шаблон или отдельный JS файл
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = submitBtn.querySelector('.spinner-border');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
                
        // Показываем спиннер
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;
        
        // Собираем данные формы
        const formData = new FormData(form);
        
        // Отправляем AJAX запрос
        fetch('needed_channel/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                window.calculationState.needed_channel = data.needed_channel
            } else {
                showError(data.error || 'Произошла ошибка при обработке запроса');
            }
        })
        // Отправляем AJAX запрос 2
        fetch('needed_channel/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                window.calculationState.needed_channel = data.needed_channel
            } else {
                showError(data.error || 'Произошла ошибка при обработке запроса');
            }
        })

        .finally(() => {
            // Скрываем спиннер
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        });

    });
});

async function processLuoTaiyan(ui) {
    const channel = ui.neededChannel.value;
    if (!channel) return;

    try {
        const response = await fetch('get_luo_taiyan/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.csrfToken },
            body: JSON.stringify({ channel })
        });
        const data = await response.json();
        
        if (data.success) {
            window.calculationState.needed_channel = data;
            ui.luoTaiyanResult.innerHTML = `<p>${data.result}</p>`;
        } else {
            alert('Ошибка (ДР): ' + data.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке данных (ДР)');
    }
}