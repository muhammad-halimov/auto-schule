// Загрузка страницы
document.addEventListener('DOMContentLoaded', async () => {
    await loadAndChangeChoices();
});

async function loadAndChangeChoices() {
    const adminOption = document.getElementById('User_roles_0');
    const studentOption = document.getElementById('User_roles_1');
    const instructorOption = document.getElementById('User_roles_2');
    const teacherOption = document.getElementById('User_roles_3');
    const carsDropDown = document.querySelector('.field-car');

    const studentFields = [
        document.getElementById('User_license'),
        document.getElementById('User_hireDate'),
        document.getElementById('User_experience'),
        document.getElementById('User_car'),
        instructorOption,
        teacherOption,
        adminOption
    ].filter(Boolean);

    const instructorFields = [
        document.getElementById('User_enrollDate'),
        document.getElementById('User_contract'),
        document.getElementById('User_examStatus'),
        studentOption,
        teacherOption,
        adminOption
    ].filter(Boolean);

    const teacherFields = [
        document.getElementById('User_enrollDate'),
        document.getElementById('User_contract'),
        document.getElementById('User_examStatus'),
        document.getElementById('User_car'),
        document.getElementById('User_license'),
        instructorOption,
        studentOption,
        adminOption
    ].filter(Boolean);

    const adminFields = [
        document.getElementById('User_enrollDate'),
        document.getElementById('User_hireDate'),
        document.getElementById('User_contract'),
        document.getElementById('User_examStatus'),
        document.getElementById('User_car'),
        document.getElementById('User_license'),
        document.getElementById('User_experience'),
        instructorOption,
        teacherOption,
        studentOption,
    ].filter(Boolean);

    const enableFields = (fields) => {
        fields.forEach(field => {
            field.disabled = false;

            // Если это HTML-элемент, меняем стили
            if (field.closest) {
                const wrapper = field.closest('.form-group, .form-field, .form-control, div');
                if (wrapper) {
                    wrapper.style.pointerEvents = 'auto';
                    wrapper.style.opacity = '1';
                }
            }
        });
    };

    const disableFields = (fields) => {
        fields.forEach(field => {
            field.disabled = true;

            if (field.closest) {
                const wrapper = field.closest('.form-group, .form-field, .form-control, div');
                if (wrapper) {
                    wrapper.style.pointerEvents = 'none';
                    wrapper.style.opacity = '0.4';
                }
            }
        });
    };

    const updateCarDropdownVisibility = () => {
        // Если выбрана роль "admin" или "teacher" — всегда блокируем
        if (adminOption.checked || teacherOption.checked) {
            carsDropDown.style.pointerEvents = 'none';
            carsDropDown.style.opacity = '0.5';
            carsDropDown.querySelectorAll('select, input').forEach(el => el.disabled = true);
            return;
        }

        // Если выбран только студент без инструктора — тоже блокируем
        if (studentOption.checked && !instructorOption.checked) {
            carsDropDown.style.pointerEvents = 'none';
            carsDropDown.style.opacity = '0.5';
            carsDropDown.querySelectorAll('select, input').forEach(el => el.disabled = true);
            return;
        }

        // Иначе — разрешаем доступ
        carsDropDown.style.pointerEvents = 'auto';
        carsDropDown.style.opacity = '1';
        carsDropDown.querySelectorAll('select, input').forEach(el => el.disabled = false);
    };

    // Инициализация при загрузке
    if (studentOption.checked) disableFields(studentFields);
    if (instructorOption.checked) disableFields(instructorFields);
    if (teacherOption.checked) disableFields(teacherFields);
    if (adminOption.checked) disableFields(adminFields);

    updateCarDropdownVisibility();

    // Обработчики событий
    studentOption.addEventListener('change', () => {
        studentOption.checked ? disableFields(studentFields) : enableFields(studentFields);
        updateCarDropdownVisibility();
    });

    instructorOption.addEventListener('change', () => {
        instructorOption.checked ? disableFields(instructorFields) : enableFields(instructorFields);
    });

    teacherOption.addEventListener('change', () => {
        teacherOption.checked ? disableFields(teacherFields) : enableFields(teacherFields);
        updateCarDropdownVisibility();
    });

    adminOption.addEventListener('change', () => {
        adminOption.checked ? disableFields(adminFields) : enableFields(adminFields);
        updateCarDropdownVisibility();
    });
}