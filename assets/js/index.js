const urlAddress = "admin-auto-schule.ru";
// const urlAddress = "127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", async () => {
    // Портфолио
    await getPortfolio();

    // Команда
    await getTeam();

    // Цены
    await getPrices();

    // Автопарк
    await getCars();
});

async function getPortfolio(){
    try {
        let response = await fetch(`https://${urlAddress}/api/reviews`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error(`Ошибка при получении портфолио. ${errorData?.error}`);
            return;
        }

        const data = await response.json();

        if (Array.isArray(data) && data.length > 0) {
            const portfolioList = document.getElementById('portfolio-wrapper');
            const portfolioModalList = document.getElementById('portfolio-modal-list');
            const limitedData = data.slice(0, 6);

            portfolioList.innerHTML = limitedData.map((portfolio, index) => {
                const image = portfolio?.image
                    ? `https://${urlAddress}/images/review_images/${portfolio.image}`
                    : 'assets/img/nav-bg.jpg';

                const title = portfolio?.title ?? 'Без названия';
                const publisherFullname = `${portfolio?.publisher?.name} ${portfolio?.publisher?.surname}` ?? 'Неизвестно';

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
                                <div class="portfolio-caption-subheading text-muted">${publisherFullname}</div>
                            </div>
                        </div>
                    </div>
                `}).join('');

            portfolioModalList.innerHTML = limitedData.map((portfolio, index) => {
                const image = portfolio?.image
                    ? `https://${urlAddress}/images/review_images/${portfolio.image}`
                    : 'assets/img/nav-bg.jpg';

                const title = portfolio?.title ?? 'Без названия';
                const description = portfolio?.description ?? 'Нет описания';
                const publisherFullname = `${portfolio?.publisher?.name} ${portfolio?.publisher?.surname}` ?? 'Неизвестно';
                const courseTitle = portfolio?.course?.title ?? 'Без курса';
                let courseOrRepresentative;

                portfolio.course || portfolio.type === "course"
                    ? courseOrRepresentative = `<li><strong>Отзыв по курсу:</strong> ${courseTitle}</li>`
                    : courseOrRepresentative =
                        `<li>
                            <strong>Отзыв преподавателю:</strong> ${portfolio.representativeFigure?.name} ${portfolio.representativeFigure?.surname}
                        </li>`;

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
                                                    <li><strong>Пользователь:</strong> ${publisherFullname}</li>
                                                    ${courseOrRepresentative}
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
    }
    catch (error) {
        console.error(`Не удалось загрузить портфолио. Ошибка: ${error.message}`);
        document.getElementById('portfolio-wrapper').innerHTML = `<p>Портфолио пока нет.</p>`;
    }
}

async function getTeam(){
    try {
        let response = await fetch(`https://${urlAddress}/api/users`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Ошибка:', errorData?.message);
            return;
        }

        const data = await response.json();

        if (Array.isArray(data) && data.length > 0) {
            const teamList = document.getElementById('team-wrapper');
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
                    ? `https://${urlAddress}/images/profile_photos/${team.image}`
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
                            ${team?.experience
                                ? `<p class="text-muted">Водительский опыт: ${team.experience} лет</p>`
                                : `<p class="text-muted">Водительский опыт: отсутствует</p>`
                            }
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            teamList.innerHTML = `<p>Команды пока нет.</p>`;
        }
    }
    catch (error) {
        console.error(`Ошибка при загрузке команды: ${error.message}`);
        document.getElementById('team-wrapper').innerHTML = `<p>Команды пока нет.</p>`;
    }
}

async function getPrices(){
    try {
        let response = await fetch(`https://${urlAddress}/api/categories_filtered/course`);

        if (!response.ok) {
            console.error(`Ошибка при загрузке цен: ${response.status} ${response.statusText}`);
            return;
        }

        const prices = await response.json();
        const limitedPrices = prices.slice(0, 6); // Исправил - нужно присвоить результат

        // Массив с цветовыми схемами Bootstrap 5
        const colorSchemes = [
            {
                header: 'bg-primary',
                badge: 'text-primary',
                price: 'text-primary',
                button: 'btn-primary'
            },
            {
                header: 'bg-success',
                badge: 'text-success',
                price: 'text-success',
                button: 'btn-success'
            },
            {
                header: 'bg-warning text-dark',
                badge: 'text-warning',
                price: 'text-warning',
                button: 'btn-warning text-dark'
            },
            {
                header: 'bg-info text-dark',
                badge: 'text-info',
                price: 'text-info',
                button: 'btn-info text-dark'
            },
            {
                header: 'bg-danger',
                badge: 'text-danger',
                price: 'text-danger',
                button: 'btn-danger'
            },
            {
                header: 'bg-secondary',
                badge: 'text-secondary',
                price: 'text-secondary',
                button: 'btn-secondary'
            }
        ];

        let pricesWrapper = document.getElementById('prices-wrapper');
        pricesWrapper.innerHTML = '';

        pricesWrapper.innerHTML = limitedPrices.map((price, index) => {
            const colors = colorSchemes[index % colorSchemes.length]; // Циклическое чередование

            return `
            <div class="col-lg-4 col-md-6">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-header ${colors.header} text-center py-4">
                        <span class="badge bg-light ${colors.badge} mb-2">${price.masterTitle}</span>
                        <h4 class="card-title mb-0">${price.title}</h4>
                    </div>
                    <div class="card-body text-center d-flex flex-column">
                        <div class="mb-4">
                            <span class="display-4 fw-bold ${colors.price}">${price.price}</span>
                            <span class="fs-5 text-muted">₽</span>
                        </div>
                        <p class="card-text text-muted mb-4 flex-grow-1">${price.description || 'Без описания'}</p>
                        <div class="mt-auto">
                            <span class="badge bg-info text-dark mb-3">Курс</span>
                            <div>
                                <a href="#contact" class="btn ${colors.button} btn-lg w-100">
                                    <i class="fas fa-shopping-cart me-2"></i>
                                    Записаться
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        }).join('');
    }
    catch (error) {
        console.error(`Ошибка при загрузке цен: ${error.message}`);
    }
}

async function getCars(){
    try {
        let response = await fetch(`https://${urlAddress}/api/cars`);

        if (!response.ok) {
            console.error(`Ошибка при загрузке автопарка: ${response.status} ${response.statusText}`);
            return;
        }

        const cars = await response.json();
        const limitedCars = cars.slice(0, 6);

        let carsWrapper = document.getElementById('autopark-wrapper');
        carsWrapper.innerHTML = '';

        // Массив с цветовыми схемами Bootstrap 5
        const colorSchemes = [
            {
                span: 'bg-primary',
                title: 'text-primary',
                button: 'btn-primary'
            },
            {
                span: 'bg-success',
                title: 'text-success',
                button: 'btn-success'
            },
            {
                span: 'bg-warning text-dark',
                title: 'text-warning text-dark',
                button: 'btn-warning text-dark'
            },
            {
                span: 'bg-danger',
                title: 'text-danger',
                button: 'btn-danger'
            },
            {
                span: 'bg-info text-dark',
                title: 'text-info text-dark',
                button: 'btn-info text-dark'
            },
            {
                span: 'bg-secondary',
                title: 'text-secondary',
                button: 'btn-secondary'
            },
        ];

        carsWrapper.innerHTML = limitedCars.map((car, index) => {
            const colors = colorSchemes[index % colorSchemes.length]; // Циклическое чередование
            let carPhoto;

            car.image
                ? carPhoto = `https://admin-auto-schule.ru/images/auto_photos/${car.image}`
                : carPhoto = `assets/img/nav-bg.jpg`

            return `
            <div class="col-lg-4 col-md-6">
                <div class="card h-100 shadow-sm border-0">
                    <div class="position-relative">
                        <img src="${carPhoto}"
                             class="card-img-top img-fluid" alt="${car.carMark.title} ${car.carModel}">
                        <div class="position-absolute top-0 end-0 m-3">
                            <span class="badge ${colors.span}">
                                ${car.category.title}
                            </span>
                        </div>
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title ${colors.title}">
                            <i class="fas fa-car me-2"></i>
                            ${car.carMark.title} ${car.carModel}
                        </h5>
                        <p class="card-text text-muted flex-grow-1">
                            ${car.category.description}
                        </p>
                        <div class="mt-auto">
                            <div class="row g-2 mb-3">
                                <div class="col-4">
                                    <small class="text-muted">
                                        <i class="fas fa-cogs me-1"></i>
                                        ${car.transmission || "Без КПП"}
                                    </small>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">
                                        <i class="fas fa-users me-1"></i>
                                        ${car.places || 0} мест
                                    </small>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">
                                        <i class="fas fa-gas-pump me-1"></i>
                                        ${car.fuelType || "Без топлива"}
                                    </small>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">
                                        <i class="fas fa-calendar me-1"></i>
                                        ${car.productionYear || 0} г.
                                    </small>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">
                                        <i class="fas fa-weight-hanging me-1"></i>
                                        ${car.weight || 0} т
                                    </small>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">
                                        <i class="fas fa-weight me-1"></i>
                                        ${car.weightLift || 0} т
                                    </small>
                                </div>
                            </div>
                            <a href="account.html" class="btn ${colors.button} w-100">
                                <i class="fas fa-info-circle me-2"></i>
                                Подробнее
                            </a>
                        </div>
                    </div>
                </div>
            </div>`;
        }).join('');
    }
    catch (error) {
        console.error(`Ошибка при загрузке автопарка: ${error.message}`);
    }
}