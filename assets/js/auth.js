window.onload = function () {
    if (localStorage.getItem('token') !== null) {
        window.location.href = 'account.html'; // Перенаправляем в личный кабинет
    }
};

document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    try {
        let response = await fetch('http://127.0.0.1:8000/api/authentication_token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        let result = await response.json();

        if (!response.ok) {
            console.error('Ошибка:', result);
            alert(result.message || 'Ошибка при авторизации');
            return;
        }

        localStorage.setItem('token', result.token);
        localStorage.setItem('email', email);   // Сохраняем email
        localStorage.setItem('password', password); // Сохраняем пароль

        console.log('Успешный вход!', result);

        window.location.href = 'account.html';
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сети. Попробуйте позже.');
    }
});