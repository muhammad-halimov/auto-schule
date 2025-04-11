window.onload = async function () {
    if (localStorage.getItem('token') === null) {
        window.location.href = 'auth.html';
    }
    await startTokenRefresh()
}

document.getElementById('logoutLink').addEventListener('click', () => {
    localStorage.removeItem('token'); // Удалить токен
    window.location.href = 'auth.html'; // Вернуться на страницу входа
});

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem('token');

    if (!token) {
        window.location.href = 'auth.html'; // Перенаправление на страницу входа
        return;
    }

    try {
        let response = await fetch('https://127.0.0.1:8000/api/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Ошибка:', await response.json());
            alert('Ошибка при получении данных. Возможно ваш аккаунт заблориван или не активирован.' + await response.json());
            localStorage.removeItem('token');
            return window.location.href = 'auth.html';
        }

        let user = await response.json();
        let userFullName = (`${user.name} ${user.surname}`);

        // Настройки профиля в ЛК
        document.getElementById('Username').value = user.username || '';
        document.getElementById('Name').value = user.name || '';
        document.getElementById('Surname').value = user.surname || '';
        document.getElementById('Patronym').value = user.patronym || '';
        document.getElementById('Phone').value = user.phone || '';
        document.getElementById('Email').value = user.email || '';
        document.getElementById('DateOfBirth').value = user.dateOfBirth || '';
        document.getElementById('AboutMe').value = user.message || '';

        // Приветственная страница в ЛК
        document.getElementById('userFullNameTopBar').innerText = userFullName || 'Default Name';
        document.getElementById('userFullNamePersonalInfoSection').innerText = userFullName || 'Default Name';
        document.getElementById('userPhonePersonalInfoSection').innerText = user.phone || '+7 999 999 99';
        document.getElementById('userEmailPersonalInfoSection').innerText = user.email || 'example@example.com';

        // Курсы в ЛК
        const coursesList = document.getElementById('courses-list');

        coursesList.innerHTML = user.courses?.length
            ? user.courses.map(course => `<li>${course.title}</li>`).join('')
            : `<li>Нет курсов</li>`;

        // Прогресс в ЛК
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сети. Попробуйте позже.');
    }
});

async function refreshToken() {
    let email = localStorage.getItem('email'); // Сохраняем email
    let password = localStorage.getItem('password'); // Сохраняем пароль

    if (!email || !password) {
        console.error('Нет сохранённых данных для повторной авторизации');
        window.location.href = 'auth.html';
        return;
    }

    try {
        let response = await fetch('https://127.0.0.1:8000/api/authentication_token', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });

        let result = await response.json();

        if (!response.ok) {
            console.error('Ошибка обновления токена:', result);
            return;
        }

        localStorage.setItem('token', result.token);
        console.log('Токен обновлён');
    } catch (error) {
        console.error('Ошибка сети при обновлении токена:', error);
    }
}

// Автообновление токена раз в 1 час (360000 мс)
function startTokenRefresh() {
    setInterval(refreshToken, 360000);
}

