document.addEventListener('DOMContentLoaded', () => {
    const adminOption = document.getElementById('User_roles_0');
    const studentOption = document.getElementById('User_roles_1');
    const instructorOption = document.getElementById('User_roles_2');
    const teacherOption = document.getElementById('User_roles_3');

    const studentFields = [
        document.getElementById('User_license'),
        document.getElementById('User_hireDate'),
        document.getElementById('User_classTitle'),
        document.getElementById('User_cars'),
        instructorOption,
        teacherOption,
        adminOption
    ].filter(Boolean);

    const instructorFields = [
        document.getElementById('User_enrollDate'),
        document.getElementById('User_classTitle'),
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
        document.getElementById('User_cars'),
        document.getElementById('User_license'),
        instructorOption,
        studentOption,
        adminOption
    ].filter(Boolean);

    const adminFields = [
        document.getElementById('User_enrollDate'),
        document.getElementById('User_hireDate'),
        document.getElementById('User_classTitle'),
        document.getElementById('User_contract'),
        document.getElementById('User_examStatus'),
        document.getElementById('User_cars'),
        document.getElementById('User_license'),
        instructorOption,
        teacherOption,
        studentOption,
    ].filter(Boolean);

    let enableFields = (fields) => fields.forEach(field => field.disabled = false);
    let disableFields = (fields) => fields.forEach(field => field.disabled = true);

    // Инициализация при загрузке
    if (studentOption.checked) disableFields(studentFields);
    if (instructorOption.checked) disableFields(instructorFields);
    if (teacherOption.checked) disableFields(teacherFields);

    // Обработчики событий
    studentOption.addEventListener('change', () => {
        studentOption.checked ? disableFields(studentFields) :  enableFields(studentFields);
    });

    instructorOption.addEventListener('change', () => {
        instructorOption.checked ? disableFields(instructorFields) :  enableFields(instructorFields);
    });

    teacherOption.addEventListener('change', () => {
        teacherOption.checked ? disableFields(teacherFields) : enableFields(teacherFields);
    });

    adminOption.addEventListener('change', () => {
        adminOption.checked ? disableFields(adminFields) : enableFields(adminFields);
    });
});