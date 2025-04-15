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

        let courses = await fetch('https://127.0.0.1:8000/api/progress', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Ошибка:', errorData.message);
            alert('Ошибка при получении данных. Возможно ваш аккаунт заблориван или не активирован. ' + errorData.message);
            localStorage.removeItem('token');
            return window.location.href = 'auth.html';
        }

        if (!courses.ok) {
            const errorData = await courses.json();
            console.error('Ошибка:', errorData.message);
            alert('Ошибка при получении курсов. ' + errorData.message);
        }

        let course = await courses.json();
        let user = await response.json();
        let userFullName = (`${user.name} ${user.surname}`);

        // Настройки профиля в ЛК
        document.getElementById('Username').value = user.username || '';
        document.getElementById('Name').value = user.name || '';
        document.getElementById('Surname').value = user.surname || '';
        document.getElementById('Patronym').value = user.patronym || '';
        document.getElementById('Phone').value = user.phone || '';
        document.getElementById('Email').value = user.email || '';
        document.getElementById('DateOfBirth').value = new Date(user.dateOfBirth).toISOString().split('T')[0] || '';
        document.getElementById('AboutMe').value = user.message || '';

        // Приветственная страница в ЛК
        document.getElementById('userFullNameTopBar').innerText = userFullName || 'Default Name';
        document.getElementById('userFullNamePersonalInfoSection').innerText = userFullName || 'Default Name';
        document.getElementById('userPhonePersonalInfoSection').innerText = user.phone || '+7 999 999 99';
        document.getElementById('userEmailPersonalInfoSection').innerText = user.email || 'example@example.com';

        // Курсы в ЛК
        const coursesList = document.getElementById('courses-list');

        coursesList.innerHTML = course.progress.byCourse?.length
            ? course.progress.byCourse.map(course => `<li>${course.courseTitle}</li>`).join('')
            : `<li>Нет курсов</li>`;

        // Прогресс в ЛК
        const progressList = document.getElementById('courses-progress');

        progressList.innerHTML = course.progress.byCourse?.length
            ? course.progress.byCourse.map(course => `
                <div class="m-b-15">
                    <h5>${course.courseTitle}<span class="pull-right">${course.percentage}%</span></h5>
                    <div class="progress">
                        <div class="progress-bar progress-bar-primary wow animated progress-animated"
                             style="width: ${course.percentage}%;">
                        </div>
                    </div>
                </div>
            `).join('')
            : `<p>Пусто</p>`;

        // Настройки аккаунта
        let accountForm = document.getElementById('accountForm');

        accountForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            let password = document.getElementById('Password').value;
            let rePassword = document.getElementById('RePassword').value;

            if (password !== rePassword) {
                alert('Пароли не совпадают.');
                return;
            }

            let data = {
                username: accountForm.username.value,
                name: accountForm.name.value,
                surname: accountForm.surname.value,
                patronym: accountForm.patronym.value,
                phone: accountForm.phone.value,
                email: accountForm.email.value,
                dateOfBirth: accountForm.dateOfBirth.value,
                message: accountForm.message.value,
                password: accountForm.password.value,
                roles: ["ROLE_STUDENT"],
            };

            for (const [key, value] of Object.entries(data)) {
                if (!value) {
                    alert(`Поле "${key}" не заполнено`);
                    return;
                }
            }

            let updateProfileReques = await fetch(`https://127.0.0.1:8000/api/update-profile`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!updateProfileReques.ok) {
                const errorData = await updateProfileReques.json();
                console.error('Ошибка:', errorData.message);
                alert('Ошибка при обновлении профиля. ' + errorData.message);
            }

            alert("Успешное обновление");
            window.location.reload();
        });

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сети. Попробуйте позже.');
        window.location.href = 'index.html';
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

