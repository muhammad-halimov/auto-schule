let form = document.getElementById('contactForm');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    let data = {
        name: form.name.value,
        phone: form.phone.value,
        email: form.email.value,
        message: form.message.value,
        roles: ["ROLE_STUDENT"],
    };

    let inputs = [
        document.getElementById('name').value,
        document.getElementById('phone').value,
        document.getElementById('email').value,
        document.getElementById('message').value,
    ];

    let submitButton = document.getElementById('submitButton');
    let successMessage = document.getElementById('submitSuccessMessage');
    let errorMessage = document.getElementById('submitErrorMessage');

    inputs.forEach(input => {
        if (input === null) submitButton.setAttribute('disabled', 'true');
    })

    try {
        let response = await fetch('http://127.0.0.1:8000/api/users', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            let errorData = await response.json();
            console.error(`Ошибка: ${response.status}`, errorData);

            // Показываем сообщение об ошибке
            let errorMessageText;

            // Проверка на дублирование email
            if (errorData.detail && errorData.detail.includes('Duplicate entry')) {
                errorMessageText = "Ошибка: Адрес электронной почты уже используется. Пожалуйста, введите другой адрес электронной почты.";
            } else {
                errorMessageText = errorData.detail || 'Произошла ошибка при отправке данных.';
            }

            errorMessage.classList.remove('d-none');
            errorMessage.innerHTML = `<div class="text-center text-danger mb-3">${errorMessageText}</div>`;
            successMessage.classList.add('d-none');
        } else {
            let result = await response.json();
            console.log('Успех:', result);

            // Показываем сообщение об успешной отправке
            successMessage.classList.remove('d-none');
            errorMessage.classList.add('d-none');
        }
    } catch (error) {
        console.error('Ошибка:', error);

        // Показываем сообщение об ошибке сети
        errorMessage.classList.remove('d-none');
        errorMessage.innerHTML = `<div class="text-center text-danger mb-3">Ошибка сети или сервера! Попробуйте позже.</div>`;
        successMessage.classList.add('d-none');
    } finally {
        // Делаем кнопку снова активной
        submitButton.disabled = false;
    }
});