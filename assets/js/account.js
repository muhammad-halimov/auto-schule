const token = localStorage.getItem('token');
const userId = localStorage.getItem('userId');
const urlAddress = "admin-auto-schule.ru";

window.onload = async () => {
    if (token === null) window.location.href = 'auth.html';
    await startTokenRefresh();
}

// Выход из профиля
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

    // Расписание
    await getSchedule()

    // Записи на вождение
    await getPersonalSchedule();
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
        document.getElementById('AboutMe').value = user.aboutMe || '';

        document.getElementById('profileImage').src = user.image
            ? `https://${urlAddress}/images/profile_photos/${user.image}`
            : "https://bootdey.com/img/Content/avatar/avatar7.png";

        // Приветственная страница в ЛК
        document.getElementById('userFullNameTopBar').innerText = userFullName || 'Default Name';
        document.getElementById('userFullNamePersonalInfoSection').innerText = userFullName || 'Default Name';
        document.getElementById('userPhonePersonalInfoSection').innerText = user.phone || '+7 999 999 99';
        document.getElementById('userEmailPersonalInfoSection').innerText = user.email || 'example@example.com';
        document.getElementById('userCategoryPersonalInfoSection').innerText = user.category?.title || 'Без категории';
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

        let progress = await progressFetch.json();
        // Курсы в ЛК (без состава)
        const coursesListPreview = document.getElementById('courses-list');

        // Список курсов на welcome странице ЛК
        coursesListPreview.innerHTML = progress.progress.byCourse?.length
            ? progress.progress.byCourse.map(course => `<li><a id="courseAnchor">${course.courseTitle}</a></li>`).join('')
            : `<li>Нет курсов</li>`;

        // Переход на вкладку курсов
        const courseAnchor = document.getElementById('courseAnchor');

        courseAnchor.addEventListener('click', (e) => {
            e.preventDefault();

            // Находим ссылку вкладки "Курсы" и программно кликаем по ней
            const coursesTabLink = document.querySelector('#coursesTab a');
            $(coursesTabLink).tab('show'); // Используем метод Bootstrap для переключения
        });

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
            formData.append('aboutMe', accountForm.message.value);

            // Only append password if it's not empty
            if (password) formData.append('password', password);

            // Append the profile photo if selected
            if (profilePhotoInput.files[0]) formData.append('profile_photo', profilePhotoInput.files[0]);

            try {
                let updateProfileFetch = await fetch(`https://${urlAddress}/api/update-profile`, {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });

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
        const coursesFetch = await fetch(`https://${urlAddress}/api/students/${userId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const coursesData = await coursesFetch.json();
        const coursesList = document.getElementById('coursesList');
        const lessonsModalContainer = document.getElementById('lessonsModal'); // Изменено название для ясности

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
                        <h5>Категория: ${course.category?.title || 'Без категории'}</h5>
                        <h5>Описание:</h5>
                        <p style="text-align: justify; padding: 2px;">${course.description || 'Без описания'}</p>
                        <p style="text-align: justify; padding: 2px;">
                            <a href="#" class="leave-review-link" data-course-id="${course.id}">Оставить отзыв</a>
                        </p>
                    </div>
                </div>
            </div>
            
            <!--Модальное окно отзыва-->
            <div class="modal fade" id="reviewModal" tabindex="-1" role="dialog" aria-labelledby="reviewModalLabel">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <form id="reviewForm" method="post" enctype="multipart/form-data">
                            <div class="modal-header">
                                <button type="button" class="close" data-dismiss="modal" aria-label="Закрыть"><span aria-hidden="true">&times;</span></button>
                                <h4 class="modal-title" id="reviewModalLabel">Оставить отзыв</h4>
                            </div>
                            <div class="modal-body">
                                <div class="form-group">
                                    <label for="reviewTitle">Заголовок отзыва</label>
                                    <input type="text" class="form-control" id="reviewTitle" name="title" required>
                                </div>
                                <div class="form-group">
                                    <label for="reviewDescription">Описание</label>
                                    <textarea class="form-control" id="reviewDescription" name="description" rows="4" required></textarea>
                                </div>
                                <div class="form-group">
                                    <label for="reviewImage">Изображение (необязательно)</label>
                                    <input type="file" id="reviewImage" name="image" accept="image/png, image/jpeg, image/jpg, image/heic">
                                </div>
                                <input type="hidden" id="courseIdForReview" name="courseId" value="${course.id}">
                            </div>
                            <div class="modal-footer">
                                <button type="submit" class="btn btn-primary">Отправить</button>
                                <button type="button" class="btn btn-default" data-dismiss="modal">Отмена</button>
                            </div>
                        </form>
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
                                    <p style="text-align: justify; padding: 2px">${lesson.description || 'Без описания'}</p>
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

        // Открытие модалки отзыва курса
        document.querySelectorAll('.leave-review-link').forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                document.getElementById('courseIdForReview').value = this.getAttribute('data-course-id');
                $('#reviewModal').modal('show');
            });
        });

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

        // Оставить отзыв
        let reviewForm = document.getElementById('reviewForm');

        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            let formData = new FormData();
            let reviewImage = document.getElementById('reviewImage');

            // formData.append('id', reviewForm.reviewId.value); для PATCH
            formData.append('title', reviewForm.title.value);
            formData.append('description', reviewForm.description.value);
            formData.append('publisher', userId);
            formData.append('course', reviewForm.courseId.value);

            if (reviewImage.files[0]) formData.append('review_image', reviewImage.files[0]);

            console.log(userId);

            try {
                const reviewFetch = await fetch(`https://${urlAddress}/api/reviews`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json',
                    },
                    body: formData
                })

                if (!reviewFetch.ok) {
                    alert(`Ошибка при отправке отзыва.`);
                    return;
                }

                alert('Отзыв успешно отправлен!');

                $('#reviewModal').modal('hide');
            }
            catch (error) {
                console.error(`Ошибка при отправке отзыва: ${error.message}`);
                alert(`Ошибка при отправке отзыва.`);
            }
        });
    } catch (error) {
        console.error(`Ошибка при загрузке курсов: ${error.message}`);
        alert(`Ошибка при загрузке курсов.`);

        // Показываем сообщение об ошибке в интерфейсе
        const coursesList = document.getElementById('coursesList');

        if (coursesList) coursesList.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function getSchedule() {
    try {
        const scheduleFetch = await fetch(`https://${urlAddress}/api/drive_schedules/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const schedule = await scheduleFetch.json();

        const scheduleBody = document.querySelector('#instructor-schedule table tbody');
        scheduleBody.innerHTML = ''; // Очистим старое содержимое

        let counter = 1;

        schedule.map(entry => {
            const matchedDates = getNextDatesForWeekDays(entry.daysOfWeek);
            const datesHtml = matchedDates.map(d => `${d.date} - ${d.day}`).join('<br>');
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${counter++}</td>
                <td>${entry.instructor.name} ${entry.instructor.surname}</td>
                <td>${datesHtml}</td>
                <td>${entry.timeFrom.slice(11, 16)} - ${entry.timeTo.slice(11, 16)}</td>
                <td>${entry.autodrome.title}</td>
                <td>${entry.category.title}</td>
                <td>${entry.category.price.price} руб</td>
                <td><button class="btn btn-success btn-xs" onclick='openModal(${JSON.stringify(entry)}, ${JSON.stringify(matchedDates)})'>Записаться</button></td>
            `;

            scheduleBody.appendChild(row);
        });

    } catch (error) {
        console.error(`Ошибка при загрузке расписания: ${error.message}`);
        alert(`Ошибка при загрузке расписания.`);
    }
}

async function getPersonalSchedule() {
    try {
        const personalScheduleFetch = await fetch(
            `https://${urlAddress}/api/instructor_lessons_filtered/${userId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const personalSchedule = await personalScheduleFetch.json();

        const personalScheduleBody = document.querySelector('#my-lessons table tbody');
        personalScheduleBody.innerHTML = ''; // Очистим старое содержимое

        let counter = 1;

        personalSchedule.map(entry => {
            const row = document.createElement('tr');

            const date = new Date(entry.date);

            const day = String(date.getUTCDate()).padStart(2, '0');
            const month = String(date.getUTCMonth() + 1).padStart(2, '0');
            const year = date.getUTCFullYear();

            const weekday = date.toLocaleDateString('ru-RU', {
                weekday: 'short',
                timeZone: 'UTC'
            }); // пн, вт и т.д.

            const formattedDate = `${day}.${month}.${year} - ${weekday}`;

            const hours = String(date.getUTCHours()).padStart(2, '0');
            const minutes = String(date.getUTCMinutes()).padStart(2, '0');
            const formattedTime = `${hours}:${minutes}`;

            row.innerHTML = `
                <td>${counter++}</td>
                <td>${entry.instructor.name} ${entry.instructor.surname}</td>
                <td>${formattedDate}</td>
                <td>${formattedTime}</td>
                <td>${entry.autodrome.title}</td>
                <td>${entry.category.title}</td>
                <td>${entry.category.price.price} руб</td>
                <td><button class="btn btn-danger btn-xs" onclick="removeDriveSchedule(${entry.id})">Отменить</button></td>
            `;

            personalScheduleBody.appendChild(row);
        });
    }
    catch (error) {
        console.error(`Ошибка при загрузке записей на вождение: ${error.message}`);
        alert(`Ошибка при загрузке записей на вождение.`);
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

// Получить даты ближайшей недели по названию дней недели
function getNextDatesForWeekDays(targetDays, daysAhead = 7) {
    const weekDaysMap = {
        "Вс": 0,
        "Пн": 1,
        "Вт": 2,
        "Ср": 3,
        "Чт": 4,
        "Пт": 5,
        "Сб": 6,
    };
    const today = new Date();
    const result = [];

    for (let i = 0; i < daysAhead; i++) {
        const date = new Date();
        date.setDate(today.getDate() + i);
        const day = date.getDay();
        const ruDay = Object.keys(weekDaysMap).find(key => weekDaysMap[key] === day);

        if (targetDays.includes(ruDay)) {
            const dayStr = date.getDate().toString().padStart(2, '0');
            const monthStr = (date.getMonth() + 1).toString().padStart(2, '0');
            const yearStr = date.getFullYear();

            result.push({
                day: ruDay,
                date: `${dayStr}.${monthStr}.${yearStr}`
            });
        }
    }

    return result;
}

// Модалка для записи на вождение
async function openModal(entry, matchedDates) {
    // Заполнение модалки
    document.getElementById('modal-instructor').textContent = `${entry.instructor.name} ${entry.instructor.surname}`;
    document.getElementById('modal-autodrome').textContent = entry.autodrome.title;
    document.getElementById('modal-category').textContent = entry.category.title;
    document.getElementById('modal-price').textContent = `${entry.category.price.price} руб`;

    // Даты
    const dateSelect = document.getElementById('modal-date');
    dateSelect.innerHTML = '';

    matchedDates.forEach(obj => {
        const option = document.createElement('option');
        option.value = obj.date;
        option.text = `${obj.date} - ${obj.day}`;
        dateSelect.appendChild(option);
    });

    // Время
    const timeFrom = entry.timeFrom.slice(11, 16);
    const timeTo = entry.timeTo.slice(11, 16);
    const timeSelect = document.getElementById('modal-time');
    timeSelect.innerHTML = '';

    // Разбиваем начальное и конечное время на часы и минуты
    let [startHour, startMinute] = timeFrom.split(':').map(Number);
    const [endHour, endMinute] = timeTo.split(':').map(Number);

    // Цикл по временным слотам с шагом 30 минут
    while (startHour < endHour || (startHour === endHour && startMinute <= endMinute)) {
        const formattedTime = `${String(startHour).padStart(2, '0')}:${String(startMinute).padStart(2, '0')}`;

        // Создаем и добавляем опцию в select
        const option = document.createElement('option');
        option.value = formattedTime;
        option.textContent = formattedTime;
        timeSelect.appendChild(option);

        // Увеличиваем время на 30 минут
        startMinute += 30;

        if (startMinute >= 60) {
            startMinute = 0;
            startHour++;
        }
    }
    $('#bookingModal').modal('show');


    // Обработка запроса
    const confirmButton = document.getElementById('confirmBooking');
    const newButton = confirmButton.cloneNode(true); // Удалить все предыдущие обработчики (через cloneNode)
    confirmButton.parentNode.replaceChild(newButton, confirmButton);

    // Теперь вешаем новый обработчик
    newButton.addEventListener('click', async (event) => {
        event.preventDefault();

        const selectedDate = document.getElementById('modal-date').value; // например: "01/05/2025"
        const selectedTime = document.getElementById('modal-time').value; // например: "14:30"

        if (!selectedDate || !selectedTime) {
            alert('Выберите дату и время.');
            return;
        }

        // Парсим дату
        const [day, month, year] = selectedDate.split('.').map(Number); // вместо '.'

        // Парсим время
        const [hours, minutes] = selectedTime.split(':').map(Number);

        // Создаём объект даты в UTC
        const dateObj = new Date(Date.UTC(year, month - 1, day, hours, minutes));

        // Проверка валидности
        if (isNaN(dateObj.getTime())) {
            alert('Некорректная дата или время.');
            return;
        }

        // Сборка тела запроса
        let lessonData = {
            "instructor": `/api/users/${entry.instructor.id}`,
            "student": `/api/users/${userId}`,
            "category": `/api/categories/${entry.category.id}`,
            "autodrome": `/api/autodromes/${entry.autodrome.id}`,
            "date": dateObj.toISOString()
        };

        try {
            await fetch(`https://${urlAddress}/api/instructor_lessons`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(lessonData)
            });

            alert('Запись успешно создана!');
            $('#bookingModal').modal('hide');

            await getPersonalSchedule();
        } catch (error) {
            console.error('Ошибка при создании записи:', error);
            alert('Ошибка при записи: ' + error.message);
        }
    });
}

// Удалить личную запись на вождение
async function removeDriveSchedule(id) {
    try {
        if (!confirm("Вы уверены, что хотите отменить запись?")) return;

        await fetch(`https://${urlAddress}/api/instructor_lessons/${id}`, {
           method: 'DELETE',
           headers: {
               'Content-Type': 'application/json',
               'Accept': '*/*',
               'Authorization': `Bearer ${token}`,
           }
        });

        await getPersonalSchedule();
    }
    catch (error) {
        console.error(`Ошибка при удалении записи на вождение: ${error.message}`);
        alert(`Ошибка при удалении записи на вождение.`);
    }
}

async function onTelegramAuth(user) {
    try {
        const tgIframe = document.getElementById('telegram-login-autoschoolmybuddybot');

        let updateUserProfileFetch = await fetch(`https://${urlAddress}/api/users/${userId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/merge-patch+json'
            },
            body: JSON.stringify({'telegramId': String(user.id)})
        });

        if (!updateUserProfileFetch.ok){
            console.error(`Ошибка при привязке профиля ТГ: ${updateUserProfileFetch.message}`);
            alert(`Ошибка при привязке профиля ТГ: ${updateUserProfileFetch.message}`);
        }

        // if (tgIframe) tgIframe.style.display = 'none';
        // await showBoundTelegramButton();
        alert("Успешная привязка");
        window.open('https://t.me/autoschoolmybuddybot?start=payload', '_blank');
    }
    catch (error) {
        console.error(`Ошибка при привязке профиля ТГ: ${error.message}`);
        alert(`Ошибка при привязке профиля ТГ: ${error.message}`);
    }
}

async function checkTelegramUser() {
    try {
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
            await showBoundTelegramButton();
        }
    }
    catch (error) {
        console.error(`Ошибка профиля ТГ: ${error.message}`);
    }
}

// let showBoundTelegramButton = async () => {
//     const accountForm = document.getElementById('accountForm');
//     const submitButton = accountForm.querySelector('button[type="submit"]');
//
//     // Удаляем старую кнопку "Профиль привязан", если есть
//     const existingBoundButton = accountForm.querySelector('button[disabled][type="button"]');
//     if (existingBoundButton) existingBoundButton.remove();
//
//     // Создаем и вставляем новую кнопку
//     const boundButton = document.createElement('button');
//     boundButton.className = 'btn btn-primary waves-effect waves-light w-md';
//     boundButton.type = 'button';
//     boundButton.disabled = true;
//     boundButton.textContent = 'Профиль привязан к ТГ';
//     boundButton.style.cssText = 'width: 225px; height: 40px; margin-bottom: 33px; margin-left: 10px;';
//     submitButton.insertAdjacentElement('afterend', boundButton);
// }