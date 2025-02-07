document.addEventListener('DOMContentLoaded', () => {
    let studentOption = document.getElementById('User_roles_1');
    let instructorOption = document.getElementById('User_roles_2');

    studentOption.addEventListener('click', (e) => {
        if (e.target.checked === true){
            document.getElementById('User_licenseNumber').setAttribute('disabled', true);
            document.getElementById('User_hireDate').setAttribute('disabled', true);
        }
        else{
            document.getElementById('User_licenseNumber').removeAttribute('disabled');
            document.getElementById('User_hireDate').removeAttribute('disabled');
        }
    });

    instructorOption.addEventListener('click', (e) => {
        if (e.target.checked === true){
            document.getElementById('User_enrollDate').setAttribute('disabled', true);
            document.getElementById('User_address').setAttribute('disabled', true);
        }
        else{
            document.getElementById('User_enrollDate').removeAttribute('disabled');
            document.getElementById('User_address').removeAttribute('disabled');
        }
    });
});