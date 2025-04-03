document.addEventListener('DOMContentLoaded', () => {
    let studentOption = document.getElementById('User_roles_1');
    let instructorOption = document.getElementById('User_roles_2');
    let teacherOption = document.getElementById('User_roles_3');

    document.querySelectorAll('.approved-switch').forEach((option) => {
        option.setAttribute('disabled', 'true');
    });

    let studentOptionsArr = [
        document.getElementById('User_license'),
        document.getElementById('User_hireDate'),
        document.getElementById('User_classTitle'),
    ];

    let instructorOptionsArr = [
        document.getElementById('User_enrollDate'),
        document.getElementById('User_classTitle'),
        document.getElementById('User_contract'),
        document.getElementById('User_examStatus'),
    ];

    let teacherOptionsArr = [
        document.getElementById('User_enrollDate'),
        document.getElementById('User_contract'),
        document.getElementById('User_examStatus'),
    ];

    studentOption.addEventListener('click', (e) => {
        if (e.target.checked) {
            studentOptionsArr.forEach((option) => {
                option.setAttribute('disabled', 'true');
            })
        } else {
            studentOptionsArr.forEach((option) => {
                option.removeAttribute('disabled');
            })
        }
    });

    instructorOption.addEventListener('click', (e) => {
        if (e.target.checked) {
            instructorOptionsArr.forEach((option) => {
                option.setAttribute('disabled', 'true');
            })
        } else {
            instructorOptionsArr.forEach((option) => {
                option.removeAttribute('disabled');
            })
        }
    });

    teacherOption.addEventListener('click', (e) => {
        if (e.target.checked) {
            teacherOptionsArr.forEach((option) => {
                option.setAttribute('disabled', 'true');
            })
        } else {
            teacherOptionsArr.forEach((option) => {
                option.removeAttribute('disabled');
            })
        }
    });
});