let form = document.getElementById('contactForm');

document.addEventListener("DOMContentLoaded", async () => {
    await getCategoryOptions();
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    let data = {
        name: form.name.value,
        surname: form.surname.value,
        phone: form.phone.value,
        email: form.email.value,
        dateOfBirth: form.dateOfBirth.value,
        message: form.message.value,
        roles: ["ROLE_STUDENT"],
        category: `/api/categories/${form.category.value}`,
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
        let response = await fetch(`https://${urlAddress}/api/users`, {
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
        }

        let result = await response.json();
        console.log('Успех:', result);

        // Показываем сообщение об успешной отправке
        successMessage.classList.remove('d-none');
        errorMessage.classList.add('d-none');
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

async function getCategoryOptions () {
    try {
        let categorySelect = document.getElementById('categorySelect')
        categorySelect.innerHTML = '';

        const categoryOptionsFetch = await fetch(`https://${urlAddress}/api/categories/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        if (!categoryOptionsFetch.ok) {
            console.error(`Ошибка при загрузке категорий: ${categoryOptionsFetch.error}`);
            alert(`Ошибка при загрузке категорий.`);
            categorySelect.disabled = true;
        }

        let categoryOptionsData = await categoryOptionsFetch.json();

        // Добавляем плейсхолдер
        const placeholderOption = document.createElement('option');

        placeholderOption.textContent = 'Выберите категорию';
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        placeholderOption.hidden = true;

        categorySelect.appendChild(placeholderOption);

        // Добавляем все категории
        categoryOptionsData.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.id;
            opt.textContent = option.title;
            categorySelect.appendChild(opt);
        });
    }
    catch (error) {
        console.error(`Ошибка при загрузке категорий: ${error.message}`);
        alert(`Ошибка при загрузке категорий.`);
        categorySelect.disabled = true;
    }
}