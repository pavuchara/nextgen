const ratingButtons = document.querySelectorAll('.rating-buttons');

ratingButtons.forEach(button => {
    button.addEventListener('click', event => {
        // Получаем значение рейтинга из data-атрибута кнопки
        const value = parseInt(event.target.dataset.value);
        const postId = parseInt(event.target.dataset.post);
        const ratingSum = button.querySelector('.rating-sum');
        // Создаем объект FormData для отправки данных на сервер
        const formData = new FormData();
        // Добавляем id статьи, значение кнопки
        formData.append('pk', postId);
        formData.append('value', value);
        // Отправляем AJAX-Запрос на сервер
        fetch("/rating/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        }).then(response => response.json())
        .then(data => {
            // Обновляем значение на кнопке
            ratingSum.textContent = data.rating_sum;
            // Обновляем стили кнопок
            updateButtonStyles(button, value);
        })
        .catch(error => console.error(error));
    });

    // Функция для обновления стилей кнопок
    function updateButtonStyles(buttonContainer, value) {
        const likeButton = buttonContainer.querySelector('[data-value="1"]');
        const dislikeButton = buttonContainer.querySelector('[data-value="-1"]');

        // Проверяем, была ли нажата кнопка лайка или дизлайка ранее
        const wasLiked = likeButton.classList.contains('btn-success');
        const wasDisliked = dislikeButton.classList.contains('btn-danger');

        // Сбрасываем стили всех кнопок
        likeButton.classList.remove('btn-outline-success', 'btn-success');
        dislikeButton.classList.remove('btn-outline-danger', 'btn-danger');

        // Устанавливаем стили в зависимости от значения рейтинга
        if (value === 1) {
            // Если лайк был уже нажат, то снимаем его
            if (wasLiked) {
                likeButton.classList.add('btn-outline-success');
                dislikeButton.classList.add('btn-outline-danger');
            } else {
                likeButton.classList.add('btn-success');
                dislikeButton.classList.add('btn-outline-danger');
            }
        } else if (value === -1) {
            // Если дизлайк был уже нажат, то снимаем его
            if (wasDisliked) {
                dislikeButton.classList.add('btn-outline-danger');
                likeButton.classList.add('btn-outline-success');
            } else {
                dislikeButton.classList.add('btn-danger');
                likeButton.classList.add('btn-outline-success');
            }
        } else {
            // Если значение рейтинга не задано или равно 0
            likeButton.classList.add('btn-outline-success');
            dislikeButton.classList.add('btn-outline-danger');
        }
    }
});
