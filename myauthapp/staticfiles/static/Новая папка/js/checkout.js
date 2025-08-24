document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('payment-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Показываем индикатор загрузки
            const submitButton = form.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Обработка...';

            // Получаем данные формы
            const formData = new FormData(form);
            
            // Отправляем данные на сервер
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.confirmation_url) {
                    // Перенаправляем на страницу подтверждения ЮKassa
                    window.location.href = data.confirmation_url;
                } else {
                    // Показываем ошибку
                    document.getElementById('card-errors').textContent = data.error || 'Произошла ошибка';
                    submitButton.disabled = false;
                    submitButton.textContent = 'Оплатить';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('card-errors').textContent = 'Ошибка соединения';
                submitButton.disabled = false;
                submitButton.textContent = 'Оплатить';
            });
        });
    }

    // Инициализация карточного виджета (если используется)
    if (document.getElementById('card-element')) {
        // Здесь может быть код для кастомного ввода карты, если ЮKassa это поддерживает
        console.log('Card element mounted');
    }
});