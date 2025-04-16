document.addEventListener("DOMContentLoaded", async () => {
    try {
        let response = await fetch('https://127.0.0.1:8000/api/reviews', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Ошибка:', errorData?.message ?? 'Неизвестная ошибка');
            alert('Ошибка при получении портфолио. ' + (errorData?.message ?? 'Что-то пошло не так.'));
            return;
        }

        const data = await response.json();
        const portfolioList = document.getElementById('portfolio-wrapper');
        const portfolioModalList = document.getElementById('portfolio-modal-list');

        if (Array.isArray(data) && data.length > 0) {
            const limitedData = data.slice(0, 6);

            portfolioList.innerHTML = limitedData.map((portfolio, index) => {
                const image = portfolio?.image
                    ? `https://127.0.0.1:8000/images/review_images/${portfolio.image}`
                    : 'assets/img/nav-bg.jpg';

                const title = portfolio?.title ?? 'Без названия';
                const publisherEmail = portfolio?.publisher?.email ?? 'Неизвестно';

                return `
                    <div class="col-lg-4 col-sm-6 mb-4">
                        <div class="portfolio-item">
                            <a class="portfolio-link" data-bs-toggle="modal" href="#portfolioModal${index + 1}">
                                <div class="portfolio-hover">
                                    <div class="portfolio-hover-content"><i class="fas fa-plus fa-3x"></i></div>
                                </div>
                                <img class="img-fluid" src="${image}" alt="${title}" />
                            </a>
                            <div class="portfolio-caption">
                                <div class="portfolio-caption-heading">${title.slice(0, 32)}</div>
                                <div class="portfolio-caption-subheading text-muted">${publisherEmail}</div>
                            </div>
                        </div>
                    </div>
                `}).join('');

            portfolioModalList.innerHTML = limitedData.map((portfolio, index) => {
                const image = portfolio?.image
                    ? `https://127.0.0.1:8000/images/review_images/${portfolio.image}`
                    : 'assets/img/nav-bg.jpg';

                const title = portfolio?.title ?? 'Без названия';
                const description = portfolio?.description ?? 'Нет описания';
                const publisherEmail = portfolio?.publisher?.email ?? 'Неизвестно';
                const categoryTitle = portfolio?.category?.title ?? 'Без категории';

                return `
                    <div class="portfolio-modal modal fade" id="portfolioModal${index + 1}" tabindex="-1" role="dialog" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="close-modal" data-bs-dismiss="modal">
                                    <img src="assets/img/close-icon.svg" alt="Close modal" />
                                </div>
                                <div class="container">
                                    <div class="row justify-content-center">
                                        <div class="col-lg-8">
                                            <div class="modal-body">
                                                <h2 class="text-uppercase">${title}</h2>
                                                <img class="img-fluid d-block mx-auto" src="${image}" alt="${title}" />
                                                <p>${description}</p>
                                                <ul class="list-inline">
                                                    <li><strong>Пользователь:</strong> ${publisherEmail}</li>
                                                    <li><strong>Категория:</strong> ${categoryTitle}</li>
                                                </ul>
                                                <button class="btn btn-primary btn-xl text-uppercase" data-bs-dismiss="modal" type="button">
                                                    <i class="fas fa-xmark me-1"></i> Закрыть
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `}).join('');
        } else {
            portfolioList.innerHTML = `<p>Портфолио пока нет.</p>`;
        }
    } catch (error) {
        console.error('Ошибка при загрузке портфолио:', error);
        alert('Не удалось загрузить портфолио.');
    }

    try {
        let response = await fetch('https://127.0.0.1:8000/api/users', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Ошибка:', errorData?.message ?? 'Неизвестная ошибка');
            alert('Ошибка при получении портфолио. ' + (errorData?.message ?? 'Что-то пошло не так.'));
            return;
        }

        const data = await response.json();
        const teamList = document.getElementById('team-wrapper');

        if (Array.isArray(data) && data.length > 0) {
            // Мапа для перевода ролей
            const roleTranslations = {
                ROLE_ADMIN: 'Администратор',
                ROLE_TEACHER: 'Преподаватель',
                ROLE_INSTRUCTOR: 'Инструктор',
                ROLE_STUDENT: 'Студент'
            };

            const translatedRole = (roles) => {
                const mainRoles = roles.filter(role => role !== 'ROLE_USER');

                if (mainRoles.length === 0)
                    return 'Пользователь';

                return mainRoles.map(role => roleTranslations[role] || role).join(', ');
            };

            const filteredData = data
                .filter(user =>
                    !user.roles.includes('ROLE_ADMIN') &&
                    !user.roles.includes('ROLE_STUDENT')
                )
                .slice(0, 3); // ограничиваем 3 пользователями

            teamList.innerHTML = filteredData.map((team) => {
                const image = team?.image
                    ? `https://127.0.0.1:8000/images/profile_photos/${team.image}`
                    : 'assets/img/user.png';

                const name = team?.name ?? 'Без имени';
                const surname = team?.surname ?? 'Без фамилии';
                const role = translatedRole(team?.roles ?? []);

                return `
        <div class="col-lg-4">
            <div class="team-member">
                <img class="mx-auto rounded-circle" src="${image}" alt="..." />
                <h4>${name} ${surname}</h4>
                <p class="text-muted">${role}</p>
                <a class="btn btn-dark btn-social mx-2" href="https://telegram.org/" target="_blank"><i class="fab fa-telegram"></i></a>
                <a class="btn btn-dark btn-social mx-2" href="https://vk.com/" target="_blank"><i class="fab fa-vk"></i></a>
            </div>
        </div>
    `;
            }).join('');
        } else {
            teamList.innerHTML = `<p>Команды пока нет.</p>`;
        }
    }
    catch (error) {
        console.error('Ошибка при загрузке команды:', error);
        alert('Не удалось загрузить команду.');
    }
});