const token = localStorage.getItem('token');
const urlAddress = "admin-auto-schule.ru";

window.onload = async () => {
    if (localStorage.getItem('token') === null)
        window.location.href = 'auth.html';

    await startTokenRefresh()
}

document.getElementById('logoutLink').addEventListener('click', async () => {
    await localStorage.removeItem('token'); // Удалить токен
    window.location.href = 'auth.html'; // Вернуться на страницу входа
});

document.addEventListener("DOMContentLoaded", async () => {
    if (!token) {
        window.location.href = 'auth.html'; // Перенаправление на страницу входа
        return;
    }

    // Данные пользователя в ЛК
    await getProfile();

    // Прогрес и курсы в ЛК
    await getProgress();

    // Настройки аккаунта
    await getProfileSettings()

    // Состав курсов
    await getCourses();

    // Смена кнопки ТГ, если пользователь аввторизован
    await checkTelegramUser();
});

async function getProfile() {
    try {
        let profileFetch = await fetch(`https://${urlAddress}/api/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!profileFetch.ok) {
            const errorData = await profileFetch.json();
            console.error(`Ошибка. Возможно ваш аккаунт заблориван или не активирован. Попробуйте заново авторизоваться. ${errorData.message}`);
            alert(`Ошибка. Возможно ваш аккаунт заблориван или не активирован. Попробуйте заново авторизоваться.`);
            localStorage.removeItem('token');
            return window.location.href = 'auth.html';
        }

        // Данные пользователя в ЛК
        let user = await profileFetch.json();
        let userFullName = (`${user.name} ${user.surname}`);

        localStorage.setItem('userId', user.id);

        // Form
        document.getElementById('Name').value = user.name || '';
        document.getElementById('Surname').value = user.surname || '';
        document.getElementById('Patronym').value = user.patronym || '';
        document.getElementById('Phone').value = user.phone || '';
        // noinspection JSCheckFunctionSignatures
        document.getElementById('DateOfBirth').value = new Date(user.dateOfBirth).toISOString().split('T')[0] || '';
        document.getElementById('AboutMe').value = user.message || '';

        document.getElementById('profileImage').src = user.image
            ? `https://${urlAddress}/images/profile_photos/${user.image}`
            : "https://bootdey.com/img/Content/avatar/avatar7.png";

        // Приветственная страница в ЛК
        document.getElementById('userFullNameTopBar').innerText = userFullName || 'Default Name';
        document.getElementById('userFullNamePersonalInfoSection').innerText = userFullName || 'Default Name';
        document.getElementById('userPhonePersonalInfoSection').innerText = user.phone || '+7 999 999 99';
        document.getElementById('userEmailPersonalInfoSection').innerText = user.email || 'example@example.com';
    } catch (error) {
        console.error(`Ошибка сети. Попробуйте позже. ${error.message}`);
        alert(`Ошибка сети. Попробуйте позже.`);
        window.location.href = 'index.html';
    }
}

async function getProgress() {
    try {
        let progressFetch = await fetch(`https://${urlAddress}/api/progress`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!progressFetch.ok) {
            const errorData = await progressFetch.json();
            console.error(`Ошибка при получении курсов или прогресса. ${errorData.message}`);
            alert(`Ошибка при получении курсов или прогресса.`);
            return;
        }

        let progress = await progressFetch.json();

        // Курсы в ЛК (без состава)
        const coursesListPreview = document.getElementById('courses-list');

        coursesListPreview.innerHTML = progress.progress.byCourse?.length
            ? progress.progress.byCourse.map(course => `<li>${course.courseTitle}</li>`).join('')
            : `<li>Нет курсов</li>`;

        // Прогресс в ЛК
        const progressList = document.getElementById('courses-progress');

        progressList.innerHTML = progress.progress.byCourse?.length
            ? progress.progress.byCourse.map(course => `
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
    } catch (error) {
        console.error(`Ошибка при получении курсов или прогресса. ${error.message}`);
        alert(`Ошибка при получении курсов или прогресса.`);
    }
}

async function getProfileSettings() {
    try {
        let accountForm = document.getElementById('accountForm');

        accountForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            let password = document.getElementById('Password').value;
            let rePassword = document.getElementById('RePassword').value;
            const profilePhotoInput = document.getElementById('ProfilePhoto');

            if (password !== rePassword) {
                alert('Пароли не совпадают.');
                return;
            }

            // Create FormData object to handle file upload
            let formData = new FormData();
            formData.append('name', accountForm.name.value);
            formData.append('surname', accountForm.surname.value);
            formData.append('patronym', accountForm.patronym.value);
            formData.append('phone', accountForm.phone.value);
            formData.append('dateOfBirth', accountForm.dateOfBirth.value);
            formData.append('message', accountForm.message.value);

            // Only append password if it's not empty
            if (password) {
                formData.append('password', password);
            }

            // Append the profile photo if selected
            if (profilePhotoInput.files[0]) {
                formData.append('profile_photo', profilePhotoInput.files[0]);
            }

            try {
                let updateProfileFetch = await fetch(`https://${urlAddress}/api/update-profile`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });

                if (!updateProfileFetch.ok) {
                    const errorData = await updateProfileFetch.json();
                    console.error(`Ошибка при обновлении профиля. ${errorData.message}`);
                    alert(`Ошибка при обновлении профиля.`);
                    return;
                }

                alert("Успешное обновление");
                window.location.reload();
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке запроса');
            }
        });
    } catch (error) {
        console.error(`Ошибка: ${error.message}`);
        alert(`Ошибка: ${error.message}`);
    }
}

async function getCourses() {
    try {
        const coursesFetch = await fetch(`https://${urlAddress}/api/students/${localStorage.getItem('userId')}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!coursesFetch.ok) {
            const errorData = await coursesFetch.json();
            new Error(errorData.message || 'Ошибка при получении данных'); // Исправлено: добавлен throw
        }

        const coursesData = await coursesFetch.json();
        const coursesList = document.getElementById('coursesList');
        const lessonsModalContainer = document.getElementById('lessonsModal'); // Изменено название для ясности

        if (!coursesList)
            new Error('Элемент coursesList не найден в DOM');

        if (!lessonsModalContainer)
            new Error('Элемент lessonsModalContainer не найден в DOM');

        if (!coursesData.courses || coursesData.courses.length === 0) {
            coursesList.innerHTML = '<p>Нет доступных курсов</p>';
            return;
        }

        // Генерация HTML для каждого курса
        coursesList.innerHTML = coursesData.courses.map((course) => `
            <div class="panel panel-default cursor-pointer" id="courseId${course.id}" style="background-color: #F5F5F5">
                <div class="panel-heading">
                    <h4 class="panel-title">
                        <a data-toggle="collapse" data-parent="#coursesAccordion" href="#course${course.id}">
                            ${course.title || 'Без названия'}
                        </a>
                    </h4>
                </div>
                <div id="course${course.id}" class="panel-collapse collapse">
                    <div class="panel-body">
                        <ul class="list-group">
                            ${course.lessons && course.lessons.length > 0
                                ? course.lessons.map(lesson => `
                                    <li class="list-group-item" data-toggle="modal" data-target="#lesson${lesson.id}Modal">
                                        <a>Урок ${lesson.orderNumber || ''}: ${lesson.title || 'Без названия'}</a>
                                        ${lesson.type === "offline" ? (lesson.date ? `<small class="text-muted">(${new Date(lesson.date).toLocaleDateString()})</small>` : '') : ""}
                                    </li>`).join('')
                                : '<li class="list-group-item">Нет доступных уроков</li>'
                            }
                        </ul>
                        <h5>Преподаватели: 
                            ${course?.lessons?.flatMap(lesson => lesson?.teacher 
                                ? `${lesson.teacher.name} ${lesson.teacher.surname}` 
                                : []).join(", ") || 'Нет преподавателей'
                            }
                        </h5>
                        <h5>Категория: ${course.category?.title ?? 'Без категории'}</h5>
                        <h5>Описание:</h5>
                        <p style="text-align: justify; padding: 2px;">${course.description ?? 'Без описания'}</p>
                    </div>
                </div>
            </div>
        `).join('');

        // Генерация модальных окон для уроков
        lessonsModalContainer.innerHTML = coursesData.courses
            .filter(course => course.lessons && course.lessons.length > 0)
            .flatMap(course => course.lessons)
            .map(lesson => `
                <div class="modal fade" id="lesson${lesson.id}Modal" tabindex="-1" aria-labelledby="lesson${lesson.id}Label" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h4 class="modal-title" id="lesson${lesson.id}Label">
                                    Урок ${lesson.orderNumber || ''}: ${lesson.title || 'Без названия'}
                                </h4>
                            </div>
                            <div class="modal-body">
                            
                                ${lesson.videos && lesson.videos.length > 0 ? `
                                    <div id="carousel-example-generic" class="carousel slide" data-ride="carousel">
                                        <!-- Wrapper for slides -->
                                        <div class="carousel-inner" role="listbox">
                                            ${lesson.videos.map((video, index) => `
                                                <div class="item ${index === 0 ? 'active' : ''}">
                                                    <video controls class="w-100" height="500" style="width: 100%;">
                                                        <source src="https://${urlAddress}/videos/lessons_videos/${video.video}" type="video/mp4">
                                                    </video>
                                                </div>
                                            `).join('')}
                                        </div>
                                    
                                        <!-- Controls -->
                                        <a class="left carousel-control" href="#carousel-example-generic" role="button" data-slide="prev">
                                            <span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>
                                            <span class="sr-only">Пред.</span>
                                        </a>
                                        <a class="right carousel-control" href="#carousel-example-generic" role="button" data-slide="next">
                                            <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
                                            <span class="sr-only">След.</span>
                                        </a>
                                    </div>
                                    <hr>` : ''
                                }
                                
                                <div>
                                    ${lesson?.teacher
                                        ? `<h5>Преподаватель: ${lesson.teacher.name} ${lesson.teacher.surname}</h5>`
                                        : '<h5>Нет преподавателей</h5>'
                                    }
                                    <h5>Описание:</h5>
                                    <p style="text-align: justify; padding: 2px">${lesson.description ?? 'Без описания'}</p>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Закрыть</button>
                                <button type="button" class="btn btn-danger mark-as-unviewed" data-lesson-id="${lesson.id}">Удалить просмотр</button>
                                <button type="button" class="btn btn-success mark-as-viewed" data-lesson-id="${lesson.id}">Отметить просмотр</button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

        // "Отметить как просмотренное"
        document.querySelectorAll('.mark-as-viewed').forEach(button => {
            button.addEventListener('click', async function() {
                const lessonId = this.getAttribute('data-lesson-id');

                try {
                    await fetch(`https://${urlAddress}/api/progress/update`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({'lessonId': lessonId})
                    });
                }
                catch (error) {
                    console.error(`Ошибка при пометке просмотра.`);
                    alert(`Ошибка при пометке просмотра: ${error.message}`);
                }

                await getProgress();

                alert("Просмотр успешно отмечен")
            });
        });

        // "Удалить просмотр"
        document.querySelectorAll('.mark-as-unviewed').forEach(button => {
            button.addEventListener('click', async function() {
                const lessonId = this.getAttribute('data-lesson-id');

                try {
                    await fetch(`https://${urlAddress}/api/progress/delete`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({'lessonId': lessonId})
                    });
                }
                catch (error) {
                    console.error(`Ошибка при пометке просмотра: ${error.message}`);
                    alert(`Ошибка при пометке просмотра.`);
                }

                await getProgress();

                alert("Просмотр успешно размечен")
            });
        });

    } catch (error) {
        console.error(`Ошибка при загрузке курсов: ${error.message}`);
        alert(`Ошибка при загрузке курсов.`);

        // Показываем сообщение об ошибке в интерфейсе
        const coursesList = document.getElementById('coursesList');

        if (coursesList)
            coursesList.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function refreshToken() {
    let email = localStorage.getItem('email'); // Сохраняем email
    let password = localStorage.getItem('password'); // Сохраняем пароль

    if (!email || !password) {
        console.error('Нет сохранённых данных для повторной авторизации');
        window.location.href = 'auth.html';
        return;
    }

    try {
        let response = await fetch(`https://${urlAddress}/api/authentication_token`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });

        let result = await response.json();

        if (!response.ok) {
            console.error(`Ошибка обновления токена: ${result}`);
            return;
        }

        localStorage.setItem('token', result.token);
        console.log('Токен обновлён');
    } catch (error) {
        console.error(`Ошибка при обновлении авторизационного токена: ${error.message}`);
        alert(`Ошибка при обновлении авторизационного токена.`)
    }
}

// Автообновление токена раз в 1 час (360000 мс)
async function startTokenRefresh() {
    setInterval(refreshToken, 360000);
}

let showBoundTelegramButton = () => {
    const accountForm = document.getElementById('accountForm');
    const submitButton = accountForm.querySelector('button[type="submit"]');

    // Удаляем старую кнопку "Профиль привязан", если есть
    const existingBoundButton = accountForm.querySelector('button[disabled][type="button"]');
    if (existingBoundButton) existingBoundButton.remove();

    // Создаем и вставляем новую кнопку
    const boundButton = document.createElement('button');
    boundButton.className = 'btn btn-primary waves-effect waves-light w-md';
    boundButton.type = 'button';
    boundButton.disabled = true;
    boundButton.textContent = 'Профиль привязан к ТГ';
    boundButton.style.cssText = 'width: 225px; height: 40px; margin-bottom: 33px; margin-left: 10px;';
    submitButton.insertAdjacentElement('afterend', boundButton);
}

async function onTelegramAuth(user) {
    try {
        const userId = localStorage.getItem('userId');
        const tgIframe = document.getElementById('telegram-login-autoschoolmybuddybot');

        let updateUserProfileFetch = await fetch(`https://${urlAddress}/api/users/${userId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/merge-patch+json'
            },
            body: JSON.stringify({'telegramId': String(user.id)})
        });

        if (tgIframe) tgIframe.style.display = 'none';
        showBoundTelegramButton();
        alert("Успешная привязка");
    }
    catch (error) {
        console.error(`Ошибка при привязке профиля ТГ: ${error.message}`);
        alert(`Ошибка при привязке профиля ТГ: ${error.message}`);
    }
}

async function checkTelegramUser() {
    try {
        const userId = localStorage.getItem('userId');

        let getUserProfileFetch = await fetch(`https://${urlAddress}/api/users/${userId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        let user = await getUserProfileFetch.json();

        if (user.telegramId) {
            const tgIframe = document.getElementById('telegram-login-autoschoolmybuddybot');
            if (tgIframe) tgIframe.style.display = 'none';
            showBoundTelegramButton();
        }
    }
    catch (error) {
        console.error(`Ошибка профиля ТГ: ${error.message}`);
    }
}