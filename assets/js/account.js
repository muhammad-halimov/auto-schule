const token = localStorage.getItem('token');
const userId = localStorage.getItem('userId');
const urlAddress = "admin-auto-schule.ru";
// const urlAddress = "127.0.0.1:8000";

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
    await getUserCourses();

    // Смена кнопки ТГ, если пользователь аввторизован
    await checkTelegramUser();

    // Расписание
    await getSchedule()

    // Записи на вождение
    await getPersonalSchedule();

    // Доступные курсы для записи
    await getAvailableCourses();

    // Транзакции пользователя
    await getUserTransactions();
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
            console.error(`Ошибка. Попробуйте заново авторизоваться. Возможно ваш не активирован. ${errorData.message}`);
            alert(`Ошибка. Попробуйте заново авторизоваться. Возможно ваш не активирован.`);
            localStorage.removeItem('token');
            return window.location.href = 'auth.html';
        }

        // Данные пользователя в ЛК
        let user = await profileFetch.json();
        let userFullName = (`${user.name} ${user.surname}`);

        localStorage.setItem('userId', user.id);

        // Form
        document.getElementById('AboutMe').value = user.aboutMe || '';

        document.getElementById('profileImage').src = user.image
            ? `https://${urlAddress}/images/profile_photos/${user.image}`
            : "https://bootdey.com/img/Content/avatar/avatar7.png";

        // Приветственная страница в ЛК
        document.getElementById('userFullNameTopBar').innerText = userFullName || 'Default Name';
        document.getElementById('userFullNamePersonalInfoSection').innerText = userFullName || 'Default Name';
        document.getElementById('userPhonePersonalInfoSection').innerText = user.phone || '+7 999 999 99';
        document.getElementById('userEmailPersonalInfoSection').innerText = user.email || 'example@example.com';
        document.getElementById('userBalance').innerText = `Ваш баланс: ${user.balance ?? 0}₽. Пополнить →` || 'Ваш баланс: 0₽. Пополнить →';

        // Баланс пользователя
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

        if (!progressFetch.ok) {
            console.error(`Ошибка при получении курсов или прогресса. Возможно, вы не подписаны ни на один курс.`);
            return;
        }

        let progress = await progressFetch.json();
        const courses = progress.combinedProgress?.byCourse || [];

        // Курсы в ЛК (без состава)
        const coursesListPreview = document.getElementById('courses-list');

        coursesListPreview.innerHTML = courses.length
            ? courses.map(course => `<li><a class="courseAnchor">${course.courseTitle}</a></li>`).join('')
            : `<li>Нет курсов</li>`;

        // Переход на вкладку курсов
        const courseAnchors = document.querySelectorAll('.courseAnchor');
        const coursesTabLink = document.querySelector('#coursesTab a');

        courseAnchors.forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                $(coursesTabLink).tab('show');
            });
        });

        // Прогресс в ЛК
        const progressList = document.getElementById('courses-progress');

        progressList.innerHTML = courses.length
            ? courses.map(course => `
                <div class="m-b-15">
                    <h5>${course.courseTitle}<span class="pull-right">${course.percentage}%</span></h5>
                    <div class="progress">
                        <div class="progress-bar progress-bar-primary wow animated progress-animated"
                             style="width: ${course.percentage}%;">
                        </div>
                    </div>
                    <ul>
                        <li>Уроки: ${course.details.lessons.percentage}%</li>
                        <li>Тесты: ${course.details.quizzes.correctPercentage}%</li>
                    </ul>
                </div>
            `).join('')
            : `<p>Пусто</p>`;
    } catch (error) {
        console.error(`Ошибка при получении курсов или прогресса. ${error.message}`);
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

                if (!updateProfileFetch.ok){
                    console.error('Ошибка:', updateProfileFetch.message);
                    return;
                }

                alert("Успешное обновление");
                window.location.reload();
            } catch (error) {
                console.error('Ошибка:', error);
            }
        });
    } catch (error) {
        console.error(`Ошибка: ${error.message}`);
        alert(`Ошибка: ${error.message}`);
    }
}

// Курсы пользователя
async function getUserCourses() {
    try {
        const availableCourses = await fetch(`https://${urlAddress}/api/courses/`);
        const coursesFetch = await fetch(`https://${urlAddress}/api/students/${userId}/`);

        if (!availableCourses.ok || !coursesFetch.ok){
            console.error(`Ошибка при получении курсов или прогресса. Возможно вы не подписаны не на один курс. ${availableCourses.message || coursesFetch.message}`);
            return;
        }

        const availableCoursesDataRaw = await availableCourses.json();
        const coursesData = await coursesFetch.json();

        // Получаем id курсов студента
        const studentCourseIds = coursesData.courses?.map(c => c.id) || [];

        // Отфильтровываем курсы
        const filteredSpeificUserCoursesData = availableCoursesDataRaw.filter(c => studentCourseIds.includes(c.id));

        const coursesList = document.getElementById('coursesList');
        const lessonsModalContainer = document.getElementById('lessonsModal'); // Изменено название для ясности
        const quizzesModalContainer = document.getElementById("quizzesModalContainer");

        // Генерация HTML для каждого курса
        coursesList.innerHTML = coursesData.courses.map((course) => `
            <div class="panel panel-default cursor-pointer" id="courseId${course.id}" style="background-color: #F5F5F5; margin: 5px 0;">
                <div class="panel-heading">
                    <h4 class="panel-title">
                        <a data-toggle="collapse" data-parent="#coursesAccordion" href="#course${course.id}">
                            ${course.title || 'Без названия'}
                        </a>
                    </h4>
                </div>
                <div id="course${course.id}" class="panel-collapse collapse">
                    <div class="panel-body">
                        <h5>Уроки</h5>
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
                        <h5>Тесты</h5>
                        <ul class="list-group">
                            ${course.courseQuizzes && course.courseQuizzes.length > 0
                                ? `<li class="list-group-item">
                                        <a href="#" class="open-quiz-modal" data-course-id="${course.id}" data-toggle="modal" data-target="#quizModal${course.id}">
                                            Открыть тесты курса
                                        </a>
                                    </li>`
                                : '<li class="list-group-item">Нет доступных тестов</li>'
                            }
                        </ul>
                        <h5>Преподаватели: 
                            ${(() => {
                                const teachers = course?.lessons
                                    ?.filter(lesson => lesson?.teacher)
                                    ?.map(lesson => lesson.teacher) || [];
                    
                                // Убираем дубликаты по id
                                const uniqueTeachersById = Array.from(
                                    new Map(teachers.map(t => [t.id, t])).values()
                                );
                    
                                return uniqueTeachersById.length > 0
                                    ? uniqueTeachersById.map(t => `${t.name} ${t.surname}`).join(', ')
                                    : 'Нет преподавателей';
                            })()}
                        </h5>
                        <h5>Категория: ${course.category?.title || 'Без категории'}</h5>
                        <h5>Описание:</h5>
                        ${course.description || 'Без описания'}
                        <div>
                            <p style="text-align: justify; padding: 2px; margin-top: 10px; margin-bottom: -10px;">
                                <a href="#" class="leave-review-link" data-course-id="${course.id}">Оставить отзыв</a>
                            </p>
                            <p style="text-align: justify; padding: 2px;">
                                <a href="#" class="course-users-link" data-course-id="${course.id}">Участники курса</a>
                            </p>
                        </div>
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

        // Модалки уроков
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
                                ${lesson.videos && lesson.videos.length > 0 
                                    ? `
                                        <div id="carouselLesson${lesson.id}" class="carousel slide" data-ride="carousel" data-interval="false">
                                            <div class="carousel-inner" role="listbox">
                                                ${lesson.videos.map((video, index) => `
                                                    <div class="item ${index === 0 ? 'active' : ''}">
                                                        <video controls class="w-100" height="500" style="width: 100%;">
                                                            <source src="https://${urlAddress}/videos/lessons_videos/${video.video}" type="video/mp4">
                                                        </video>
                                                    </div>
                                                `).join('')}
                                            </div>
                                            <div class="text-center" style="margin-top: 15px;">
                                                <a class="btn btn-default" href="#carouselLesson${lesson.id}" data-slide="prev">
                                                    <span class="glyphicon glyphicon-chevron-left"></span> Назад
                                                </a>
                                                <a class="btn btn-default" href="#carouselLesson${lesson.id}" data-slide="next">
                                                    Вперёд <span class="glyphicon glyphicon-chevron-right"></span>
                                                </a>
                                            </div>
                                        </div>
                                        <hr>` 
                                    : ''
                                }
                                <div>
                                    ${lesson?.teacher
                                        ? `<h5>Преподаватель: ${lesson.teacher.name} ${lesson.teacher.surname}</h5>`
                                        : '<h5>Нет преподавателей</h5>'
                                    }
                                    <h5>Описание:</h5>
                                    ${lesson.description || 'Без описания'}
                                </div>
                            </div>
                            <div class="modal-footer">
                                <div class="row">
                                    <div class="col-xs-12 col-sm-4">
                                        <button style="margin: 2px;" type="button" class="btn btn-success btn-block mark-as-viewed" data-lesson-id="${lesson.id}">Отметить просмотр</button>
                                    </div>
                                    <div class="col-xs-12 col-sm-4">
                                        <button style="margin: 2px;" type="button" class="btn btn-danger btn-block mark-as-unviewed" data-lesson-id="${lesson.id}">Удалить просмотр</button>
                                    </div>
                                    <div class="col-xs-12 col-sm-4">
                                        <button style="margin: 2px;" type="button" class="btn btn-default btn-block" data-dismiss="modal">Закрыть</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

        // Модалки тестов
        quizzesModalContainer.innerHTML += coursesData.courses
            .filter(course => course.courseQuizzes && course.courseQuizzes.length > 0)
            .map(course => `
                <div class="modal fade" id="quizModal${course.id}" tabindex="-1" role="dialog" aria-labelledby="quizModalLabel${course.id}">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h4 class="modal-title" id="quizModalLabel${course.id}">Тесты по курсу "${course.title}"</h4>
                            </div>
                            <div class="modal-body">
                                <div id="quizCarousel${course.id}" class="carousel slide" data-ride="carousel" data-interval="false">
                                    <div class="carousel-inner">
                                        ${course.courseQuizzes.map((quiz, index) => `
                                            <div class="item ${index === 0 ? 'active' : ''}">
                                                <div class="quiz-slide panel panel-default" style="padding: 15px; border: 1px solid #ccc; border-radius: 8px; margin-bottom: 15px;">
                                                    <h5><strong>Вопрос ${quiz.orderNumber || (index + 1)}:</strong></h5>
                                                    <p>${quiz.question}</p>
        
                                                    ${quiz.image ? `
                                                        <div style="border: 1px solid #ccc; border-radius: 5px; padding: 5px; margin: 10px 0; text-align: center;">
                                                            <img src="https://${urlAddress}/images/quiz_photos/${quiz.image}" alt="Quiz image" style="max-width: 100%; height: auto;">
                                                        </div>
                                                    ` : ''}
        
                                                    <form>
                                                        ${quiz.answers.map(answer => `
                                                            <div class="radio">
                                                                <label>
                                                                    <input type="radio" name="quiz${quiz.id}" value="${answer.id}">
                                                                    ${answer.answerText}
                                                                </label>
                                                            </div>
                                                        `).join('')}
                                                    </form>
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
        
                                    <div class="text-center" style="margin-top: 20px;">
                                        <a class="btn btn-default" href="#quizCarousel${course.id}" data-slide="prev">
                                            <span class="glyphicon glyphicon-chevron-left"></span> Назад
                                        </a>
                                        <a class="btn btn-default" href="#quizCarousel${course.id}" data-slide="next">
                                            Вперёд <span class="glyphicon glyphicon-chevron-right"></span>
                                        </a>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="submit" class="btn btn-success" data-dismiss="modal">Закончить</button>
                                <button type="button" class="btn btn-default" data-dismiss="modal">Закрыть</button>
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

        // Открытие модалки группы
        document.querySelectorAll('.course-users-link').forEach(link => {
            link.addEventListener('click', async function(e) {
                e.preventDefault();

                const courseId = this.getAttribute('data-course-id');
                const modalBody = document.getElementById('courseUsersModalTableBody');
                modalBody.innerHTML = '<tr><td>Загрузка данных...</td></tr>';

                $('#courseUsersModal').modal('show');

                try {
                    // Получаем данные курса
                    const response = await fetch(`https://${urlAddress}/api/courses/${courseId}`);

                    if (!response.ok) {
                        new Error(`Ошибка HTTP: ${response.status}`);
                    }

                    const currentCourse = await response.json();
                    modalBody.innerHTML = '';

                    if (currentCourse.users && currentCourse.users.length > 0) {
                        currentCourse.users.forEach(user => {
                            const userRow = document.createElement('tr');
                            userRow.className = 'candidates-list';
                            userRow.innerHTML = `
                                <td class="title">
                                    <div class="thumb">
                                        ${user?.image
                                        ? `<img class="img-fluid" src="https://${urlAddress}/images/profile_photos/${user.image}" alt="${user.name} ${user.surname}">`
                                        : `<img class="img-fluid" src="https://bootdey.com/img/Content/avatar/avatar7.png" alt="${user.name} ${user.surname}">`
                                    }
                                    </div>
                                    <div class="candidate-list-details">
                                        <div class="candidate-list-info">
                                            <div class="candidate-list-title">
                                                <h5 class="mb-0"><a>${user.name} ${user.surname}</a></h5>
                                            </div>
                                            <div class="candidate-list-option">
                                                <ul class="list-unstyled">
                                                    <li><i class="fa fa-filter pr-1"></i> ${user?.aboutMe || "Без био"}</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            `;
                            modalBody.appendChild(userRow);
                        });
                    } else {
                        modalBody.innerHTML = '<tr><td>Нет участников в этом курсе</td></tr>';
                    }
                } catch (error) {
                    console.error('Ошибка при загрузке участников курса:', error);
                    modalBody.innerHTML = '<tr><td>Ошибка при загрузке данных</td></tr>';
                }
            });
        });

        // "Отметить как просмотренное"
        document.querySelectorAll('.mark-as-viewed').forEach(button => {
            button.addEventListener('click', async function() {
                const lessonId = this.getAttribute('data-lesson-id');

                try {
                    await fetch(`https://${urlAddress}/api/progress/lesson/update`, {
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
                    return;
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
                    await fetch(`https://${urlAddress}/api/progress/lesson/delete`, {
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
                    return;
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
            formData.append('type', 'course');

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

        // Отправка тестов
        const savedAnswers = JSON.parse(localStorage.getItem('quizAnswers') || '{}');

        document.querySelectorAll('.modal .btn-success[data-dismiss="modal"]').forEach(button => {
            button.addEventListener('click', async function (e) {
                const modal = this.closest('.modal');
                const carousel = modal.querySelector('.carousel-inner');
                const quizItems = carousel.querySelectorAll('.quiz-slide');

                const quizResults = [];

                quizItems.forEach(item => {
                    const quizIdMatch = item.closest('.item').querySelector('form input[type="radio"]')?.name?.match(/quiz(\d+)/);
                    if (!quizIdMatch) return;

                    const quizId = parseInt(quizIdMatch[1]);
                    const selectedAnswers = Array.from(item.querySelectorAll('input[type="radio"]:checked')).map(input => parseInt(input.value));

                    if (selectedAnswers.length > 0) {
                        quizResults.push({
                            quizId: quizId,
                            answers: selectedAnswers
                        });
                    }
                });

                if (quizResults.length === 0) {
                    alert("Вы не выбрали ни одного ответа.");
                    return;
                }

                try {
                    const response = await fetch(`https://${urlAddress}/api/progress/quiz/batch-update`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(quizResults)
                    });

                    if (!response.ok) {
                        const errMsg = await response.text();
                        console.error(`Ошибка при отправке ответов: ${errMsg}`);
                        alert("Произошла ошибка при отправке ответов.");
                        return;
                    }

                    alert("Ответы успешно отправлены!");
                    await getProgress();
                } catch (err) {
                    console.error(`Ошибка запроса: ${err.message}`);
                    alert("Ошибка отправки данных.");
                }
            });
        });

        document.querySelectorAll('.quiz-slide input[type="radio"]').forEach(input => {
            input.addEventListener('change', function () {
                const quizId = this.name.replace('quiz', '');
                const selected = document.querySelector(`input[name="quiz${quizId}"]:checked`);
                if (!selected) return;

                // Сохраняем выбор в localStorage
                const saved = JSON.parse(localStorage.getItem('quizAnswers') || '{}');
                saved[quizId] = [parseInt(selected.value)];
                localStorage.setItem('quizAnswers', JSON.stringify(saved));
            });
        });

        Object.entries(savedAnswers).forEach(([quizId, answers]) => {
            answers.forEach(answerId => {
                const input = document.querySelector(`input[name="quiz${quizId}"][value="${answerId}"]`);
                if (input) {
                    input.checked = true;
                }
            });
        });
    } catch (error) {
        console.error(`Ошибка при получении курсов или прогресса. Возможно вы не подписаны не на один курс. ${error.message}`);

        // Показываем сообщение в интерфейсе
        const coursesList = document.getElementById('coursesList');
        if (coursesList) coursesList.innerHTML = `<div class="alert alert-warning">Нет курсов</div>`;
    }
}

// Доступные курсы
async function getAvailableCourses() {
    try {
        const availableCourses = await fetch(`https://${urlAddress}/api/courses/`)
        const studentCoursesFetch = await fetch(`https://${urlAddress}/api/students/${userId}/`);

        if (!availableCourses.ok || !studentCoursesFetch.ok) {
            console.error(`Ошибка при загрузке доступных курсов: ${availableCourses.message || studentCoursesFetch.message}`);
            return;
        }

        const availableCoursesDataRaw = await availableCourses.json();
        const studentData = await studentCoursesFetch.json();

        // Получаем id курсов студента
        const studentCourseIds = studentData.courses?.map(c => c.id) || [];

        // Отфильтровываем курсы, исключая те, что уже есть у студента
        const availableCoursesData = availableCoursesDataRaw.filter(c => !studentCourseIds.includes(c.id));
        const availableCoursesHtml = document.getElementById('coursesListAvailable');
        const availableCoursesLessonsModal = document.getElementById('availableCoursesLessonsModal');

        if (availableCoursesData.length === 0) {
            availableCoursesHtml.innerHTML = `<div class="alert alert-warning">Нет курсов</div>`;
            return;
        }

        // Генерация HTML доступных курсов
        availableCoursesHtml.innerHTML = availableCoursesData.map((availableCourse) => `
            <div class="panel panel-default cursor-pointer" id="courseId${availableCourse.id}" style="background-color: #F5F5F5; margin: 5px 0;">
                <div class="panel-heading">
                    <h4 class="panel-title">
                        <a data-toggle="collapse" href="#courseAvailableId${availableCourse.id}">
                            ${availableCourse.title || 'Без названия'}
                        </a>
                    </h4>
                </div>
                <div id="courseAvailableId${availableCourse.id}" class="panel-collapse collapse">
                    <div class="panel-body">
                        <h5>Уроков ${availableCourse.lessons.length} шт</h5>
                        <ul class="list-group">
                            ${availableCourse.lessons && availableCourse.lessons.length > 0
                                ? availableCourse.lessons.map(lesson => `
                                    <li class="list-group-item" data-toggle="modal" data-target="#availableLesson${lesson.id}Modal">
                                        <a>Урок ${lesson.orderNumber || ''}: ${lesson.title || 'Без названия'}</a>
                                        ${lesson.type === "offline" ? (lesson.date ? `<small class="text-muted">(${new Date(lesson.date).toLocaleDateString()})</small>` : '') : ""}
                                    </li>`).join('')
                                : '<li class="list-group-item">Нет доступных уроков</li>'
                            }
                        </ul>
                        <h5>Тестов ${availableCourse.courseQuizzes.length} шт</h5>
                        <h5>Преподаватели: 
                            ${(() => {
                                const teachers = availableCourse?.lessons
                                    ?.filter(lesson => lesson?.teacher)
                                    ?.map(lesson => lesson.teacher) || [];
                    
                                // Убираем дубликаты по id
                                const uniqueTeachersById = Array.from(
                                    new Map(teachers.map(t => [t.id, t])).values()
                                );
                    
                                return uniqueTeachersById.length > 0
                                    ? uniqueTeachersById.map(t => `${t.name} ${t.surname}`).join(', ')
                                    : 'Нет преподавателей';
                            })()}
                        </h5>
                        <h5>Цена: ${availableCourse.category.price || 0} руб</h5>
                        <input type="hidden" value="${availableCourse.category.price}" id="course-price"/>
                        <h5>Категория: ${availableCourse.category?.title || 'Без категории'}</h5>
                        <h5>Описание:</h5>
                        <p style="text-align: justify; margin-top: -8px; margin-bottom: 10px; margin-left: 3px;">${availableCourse.description || 'Без описания'}</p>
                        <button class="btn btn-success btn-xs mt-1" onclick='openAvailableCourseModal(${JSON.stringify(availableCourse)})'>Записаться</button>
                    </div>
                </div>
            </div>
        `).join('');

        // Генерация модальных окон доступных курсов
        availableCoursesLessonsModal.innerHTML = availableCoursesData
            .filter(course => course.lessons && course.lessons.length > 0)
            .flatMap(course => course.lessons)
            .map(lesson => `
                <div class="modal fade" id="availableLesson${lesson.id}Modal" tabindex="-1" aria-labelledby="lesson${lesson.id}Label" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h4 class="modal-title" id="lesson${lesson.id}Label">
                                    Урок ${lesson.orderNumber || ''}: ${lesson.title || 'Без названия'}
                                </h4>
                            </div>
                            <div class="modal-body">
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
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
    }
    catch (error) {
        console.error(`Ошибка при загрузке доступных курсов: ${error.message}`);
        const coursesListAvailable = document.getElementById('coursesListAvailable');
        if (coursesListAvailable) coursesListAvailable.innerHTML = `<div class="alert alert-warning">Нет курсов</div>`;
    }
}

async function getSchedule() {
    try {
        const scheduleFetch = await fetch(`https://${urlAddress}/api/drive_schedules/`);

        if (!scheduleFetch.ok) {
            console.error(`Ошибка при загрузке расписания: ${scheduleFetch.message}`);
            return;
        }

        const schedule = await scheduleFetch.json();

        const scheduleBody = document.querySelector('#instructor-schedule table tbody');
        scheduleBody.innerHTML = ''; // Очистим старое содержимое

        let counter = 1;

        schedule?.map(entry => {
            const matchedDates = getNextDatesForWeekDays(entry?.daysOfWeek);
            const datesHtml = matchedDates.map(d => `${d?.date} - ${d?.day}`).join('<br>');
            const row = document.createElement('tr');
            let carImage = `<p>${entry?.instructor.car?.carMark?.title} ${entry?.instructor.car?.carModel}</p>`;

            if(entry.instructor.car.image){
                carImage = `<a href="https://${urlAddress}/images/auto_photos/${entry?.instructor.car?.image}" target="_blank">${entry?.instructor.car?.carMark?.title} ${entry?.instructor.car?.carModel}</a>`;
            }

            row.innerHTML = `
                <td>${counter++}</td>
                <td><a href="" id="instructor-review-anchor">${entry?.instructor.name} ${entry?.instructor.surname}</a></td>
                <td>${carImage}</td>
                <td>${datesHtml}</td>
                <td>${entry?.timeFrom?.slice(11, 16)} - ${entry.timeTo?.slice(11, 16)}</td>
                <td>${entry?.autodrome?.title}</td>
                <td>${entry?.category?.title}</td>
                <td>${entry?.category?.price} руб</td>
                <td><button class="btn btn-success btn-xs" onclick='openScheduleModal(${JSON.stringify(entry)}, ${JSON.stringify(matchedDates)})'>Записаться</button></td>
            `;

            scheduleBody.appendChild(row);
        });

    } catch (error) {
        console.error(`Ошибка при загрузке расписания: ${error.message}`);
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

        if (!personalScheduleFetch.ok) {
            console.error(`Ошибка при загрузке записей на вождение: ${personalScheduleFetch.message}`);
            return;
        }

        const personalSchedule = await personalScheduleFetch.json();

        const personalScheduleBody = document.querySelector('#my-lessons table tbody');
        personalScheduleBody.innerHTML = ''; // Очистим старое содержимое

        let counter = 1;

        personalSchedule?.map(entry => {
            const row = document.createElement('tr');

            const date = new Date(entry?.date);

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
            let carImage = `<p>${entry?.instructor.car?.carMark?.title} ${entry?.instructor.car?.carModel}</p>`;

            if(entry.instructor.car.image){
                carImage = `<a href="https://${urlAddress}/images/auto_photos/${entry?.instructor.car?.image}" target="_blank">${entry?.instructor.car?.carMark?.title} ${entry?.instructor.car?.carModel}</a>`;
            }

            row.innerHTML = `
                <td>${counter++}</td>
                <td><a href="" id="instructor-review-anchor">${entry?.instructor.name} ${entry?.instructor.surname}</a></td>
                <td>${carImage}</td>
                <td>${formattedDate}</td>
                <td>${formattedTime}</td>
                <td>${entry?.autodrome.title}</td>
                <td>${entry?.category.title}</td>
                <td>${entry?.category.price} руб</td>
                <td><button class="btn btn-danger btn-xs" onclick="removeDriveSchedule(${entry.id})">Отменить</button></td>
            `;

            personalScheduleBody.appendChild(row);
        });
    }
    catch (error) {
        console.error(`Ошибка при загрузке записей на вождение: ${error.message}`);
    }
}

async function getUserTransactions() {
    try {
        const response = await fetch(
            `https://${urlAddress}/api/transactions_filtered/${userId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

        if (!response.ok) {
            console.error(`Ошибка при загрузке транзакций: ${response.status} ${response.statusText}`);
            return;
        }

        const transactions = await response.json();
        const invoiceTableBody = document.getElementById('invoice-table-body');
        const paymentForm = document.getElementById('paymentForm');

        invoiceTableBody.innerHTML = '';

        // Рендер историй транзакций
        invoiceTableBody.innerHTML = transactions.map((t, i) => {
            const date = new Date(t.transactionDatetime).toLocaleDateString('ru-RU');
            const shortDesc = (t.course.description || '').slice(0, 30);
            return `
                <tr>
                    <td class="no">${i + 1}</td>
                    <td class="text-left">
                        <h3>${t.course.title}</h3>
                        ${shortDesc}...
                    </td>
                    <td class="unit">${date}</td>
                    <td class="qty">${t.course.category.title}</td>
                    <td class="unit">${t.course.lessonsCount}</td>
                    <td class="qty">${t.course.courseQuizzesCount}</td>
                    <td class="total">₽${t.course.category.price}</td>
                </tr>
            `;
        }).join('');

        // Обработка формы пополнения кошелка
        paymentForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const amount = parseFloat(document.getElementById('balanceAmount').value);

            if (isNaN(amount) || amount <= 0) return;

            try {
                const studentFetch = await fetch(`https://${urlAddress}/api/students/${userId}`);
                const studentData = await studentFetch.json();
                const totalBalance = (parseFloat(studentData.balance) + amount);

                const paymentUpdateRequest = await fetch(`https://${urlAddress}/api/users/${userId}`, {
                    method: 'PATCH',
                    headers: {
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/merge-patch+json'
                    },
                    body: JSON.stringify({ balance: String(totalBalance) })
                });

                if (!paymentUpdateRequest.ok || !studentFetch.ok) {
                    console.error(`Ошибка при пополнении: ${paymentUpdateRequest.statusText || studentFetch.statusText}`);
                    return;
                }

                alert(`Баланс успешно пополнен на ${amount}₽`);

                // Очистить поле
                document.getElementById('balanceAmount').value = '';

                // Закрыть модалку
                $('#paymentModal').modal('hide');

                // Обновить данные пользователя
                await getProfile();

            } catch (error) {
                alert(`Ошибка при пополнении: ${error.message}`);
                console.error(error);
            }
        });
    }
    catch (error) {
        console.error(`Ошибка при загрузке транзакций: ${error.message}`);
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

        if (!response.ok) {
            console.error(`Ошибка обновления токена: ${result}`);
            alert(`Ошибка обновления токена.`);
            return;
        }

        let result = await response.json();

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
async function openScheduleModal(entry, matchedDates) {
    const allScheduleFetch = await fetch(`https://${urlAddress}/api/instructor_lessons`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    if (!allScheduleFetch.ok) {
        console.error(`Ошибка при загрузке расписания: ${allScheduleFetch.message}`);
        return;
    }

    const allSchedule = await allScheduleFetch.json();

    // Заполнение модалки
    document.getElementById('modal-instructor').textContent = `${entry.instructor.name} ${entry.instructor.surname}`;
    document.getElementById('modal-autodrome').textContent = entry.autodrome.title;
    document.getElementById('modal-category').textContent = entry.category.title;
    document.getElementById('modal-price').textContent = `${entry.category.price.price} руб`;

    // Даты
    const dateSelect = document.getElementById('modal-date');
    dateSelect.innerHTML = '';

    matchedDates.map(obj => {
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

    // Получаем выбранную дату
    const selectedDateRaw = matchedDates[0]?.date; // напр. "19.05.2025"
    const [selDay, selMonth, selYear] = selectedDateRaw.split('.').map(Number);

    let [startHour, startMinute] = timeFrom.split(':').map(Number);
    const [endHour, endMinute] = timeTo.split(':').map(Number);

    // Собираем все занятые временные слоты на выбранную дату для текущего инструктора, автодрома и категории
    const busyTimes = allSchedule
        .filter(lesson => {
            const lessonDate = new Date(lesson.date);

            const isSameInstructor = lesson.instructor.id === entry.instructor.id;
            const isSameAutodrome = lesson.autodrome.id === entry.autodrome.id;
            const isSameCategory = lesson.category.id === entry.category.id;

            const isSameDay =
                lessonDate.getUTCFullYear() === selYear &&
                lessonDate.getUTCMonth() === selMonth - 1 &&
                lessonDate.getUTCDate() === selDay;

            return isSameInstructor && isSameAutodrome && isSameCategory && isSameDay;
        })
        .map(lesson => {
            const dateObj = new Date(lesson.date);
            return `${String(dateObj.getUTCHours()).padStart(2, '0')}:${String(dateObj.getUTCMinutes()).padStart(2, '0')}`;
        });

    let hasFreeSlot = false;

    while (startHour < endHour || (startHour === endHour && startMinute <= endMinute)) {
        const formattedTime = `${String(startHour).padStart(2, '0')}:${String(startMinute).padStart(2, '0')}`;

        if (!busyTimes.includes(formattedTime)) {
            const option = document.createElement('option');
            option.value = formattedTime;
            option.textContent = formattedTime;
            timeSelect.appendChild(option);
            hasFreeSlot = true;
        }

        startMinute += 30;
        if (startMinute >= 60) {
            startMinute = 0;
            startHour++;
        }
    }

    // Если нет свободных слотов
    if (!hasFreeSlot) {
        const option = document.createElement('option');
        option.disabled = true;
        option.selected = true;
        option.textContent = 'Нет доступного времени';
        timeSelect.appendChild(option);
    }
    $('#bookingModal').modal('show');


    // Обработка запроса
    const confirmButton = document.getElementById('confirmBooking');
    const newButton = confirmButton.cloneNode(true); // Удалить все предыдущие обработчики (через cloneNode)
    confirmButton.parentNode.replaceChild(newButton, confirmButton);

    // Теперь вешаем новый обработчик
    newButton.addEventListener('click', async (event) => {
        event.preventDefault();

        const selectedDate = document.getElementById('modal-date').value; // например: "01.05.2025"
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

// Модалка для записи на курс
async function openAvailableCourseModal(entry) {
    document.getElementById('modal-course-title').textContent = entry.title || 'Без названия';
    document.getElementById('modal-course-category').textContent = entry.category?.title || 'Без категории';
    document.getElementById('modal-course-price').textContent = `${entry.category.price || 0} руб`;
    document.getElementById('modal-course-description').textContent = entry.description || 'Без описания';
    document.getElementById('modal-course-lesson-count').textContent = `${entry.lessons?.length || 0} шт`;

    $('#bookingCourseModal').modal('show');

    // Обработка запроса
    const confirmButton = document.getElementById('confirmCourseBooking');
    const newButton = confirmButton.cloneNode(true); // Удалить все предыдущие обработчики (через cloneNode)
    confirmButton.parentNode.replaceChild(newButton, confirmButton);

    newButton.addEventListener('click', async (event) => {
        event.preventDefault();

        try {
            const coursesFetch = await fetch(`https://${urlAddress}/api/courses/${entry.id}`);
            const studentFetch = await fetch(`https://${urlAddress}/api/students/${userId}`);
            const coursePrice = document.getElementById('course-price').value;

            const courseObject = {
                "user": `/api/users/${userId}`,
                "course": `/api/courses/${entry.id}`
            }

            if (!coursesFetch.ok || !studentFetch.ok) {
                console.error(`Ошибка при получении данных курса или пользователя. ${coursesFetch.statusText || studentFetch.statusText}`);
                return;
            }

            const courseData = await coursesFetch.json();
            const studentData = await studentFetch.json();

            if (studentData.balance < coursePrice) {
                alert("Недостаточно средств на балансе!");
                return;
            }

            // Преобразуем пользователей курса в массив IRI
            const currentUserLinks = (courseData.users || []).map(user =>
                typeof user === 'string'
                    ? user
                    : `/api/users/${user.id}`
            );

            // Добавляем текущего пользователя, если его ещё нет
            const currentUserIri = `/api/users/${userId}`;

            if (!currentUserLinks.includes(currentUserIri)) currentUserLinks.push(currentUserIri);

            // Обновляем курс
            const coursesPatchRequest = await fetch(`https://${urlAddress}/api/courses/${entry.id}`, {
                method: 'PATCH',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/merge-patch+json'
                },
                body: JSON.stringify({ users: currentUserLinks })
            });

            // Обновляем баланс пользователя
            const userPatchRequest = await fetch(`https://${urlAddress}/api/users/${userId}`, {
                method: 'PATCH',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/merge-patch+json'
                },
                body: JSON.stringify({ balance: String(studentData.balance - coursePrice) }),
            });

            // Обновляем баланс пользователя
            const transactionsPostRequest = await fetch(`https://${urlAddress}/api/transactions`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(courseObject)
            });

            if (!coursesPatchRequest.ok || !userPatchRequest.ok || !transactionsPostRequest.ok) {
                console.error(`Ошибка при обновлении курса. ${coursesPatchRequest.statusText || userPatchRequest.statusText || transactionsPostRequest.statusText}`);
                return;
            }

            alert('Запись прошла успешно!');
            $('#bookingCourseModal').modal('hide');

            await getAvailableCourses();
            await getUserCourses();
            await getProgress();
            await getProfile();
            await getUserTransactions();
        } catch (error) {
            console.error(`Ошибка при записи на курс. ${error.message}`);
            alert(`Ошибка при записи на курс.`);
        }
    });
}

// Удалить личную запись на вождение
async function removeDriveSchedule(id) {
    try {
        if (!confirm("Вы уверены, что хотите отменить запись?")) return;

        const deleteResponse = await fetch(`https://${urlAddress}/api/instructor_lessons/${id}`, {
           method: 'DELETE',
           headers: {
               'Content-Type': 'application/json',
               'Accept': '*/*',
               'Authorization': `Bearer ${token}`,
           }
        });

        if (!deleteResponse.ok){
            console.error(`Ошибка при удалении записи на вождение: ${deleteResponse.message}`);
            return;
        }

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
            return;
        }

        if (tgIframe) tgIframe.style.display = 'none';
        await showBoundTelegramButton();
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
        let getUserProfileFetch = await fetch(`https://${urlAddress}/api/users/${userId}`);

        if (!getUserProfileFetch.ok){
            console.error(`Ошибка профиля ТГ: ${getUserProfileFetch.message}`);
            return;
        }

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

let showBoundTelegramButton = async () => {
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