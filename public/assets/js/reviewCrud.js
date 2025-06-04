// Загрузка страницы
document.addEventListener('DOMContentLoaded', async () => {
    await loadAndChangeChoices();
});

async function loadAndChangeChoices() {
    const courseOption = document.getElementById('Review_type_0');
    const representativeOption = document.getElementById('Review_type_1');

    const courseDropDown = document.querySelector('.course-field');
    const representativeDropDown = document.querySelector('.representative-field');

    const disableDropDown = (dropDown) => {
        dropDown.style.pointerEvents = 'none';
        dropDown.style.opacity = '0.4';
        dropDown.querySelectorAll('select, input, textarea').forEach(el => el.disabled = true);
    };

    const enableDropDown = (dropDown) => {
        dropDown.style.pointerEvents = 'auto';
        dropDown.style.opacity = '1';
        dropDown.querySelectorAll('select, input, textarea').forEach(el => el.disabled = false);
    };

    const updateDropDowns = () => {
        if (courseOption.checked) {
            enableDropDown(courseDropDown);
            disableDropDown(representativeDropDown);
        } else if (representativeOption.checked) {
            enableDropDown(representativeDropDown);
            disableDropDown(courseDropDown);
        } else {
            // Если ничего не выбрано — отключаем оба
            disableDropDown(courseDropDown);
            disableDropDown(representativeDropDown);
        }
    };

    // Инициализация при загрузке
    updateDropDowns();

    // Обработчики переключения
    courseOption.addEventListener('change', updateDropDowns);
    representativeOption.addEventListener('change', updateDropDowns);
}