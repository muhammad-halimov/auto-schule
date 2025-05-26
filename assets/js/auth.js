const urlAddress = "admin-auto-schule.ru";
// const urlAddress = "127.0.0.1:8000";

window.onload = async () => {
    if (localStorage.getItem('token') !== null) {
        window.location.href = 'account.html'; // Перенаправляем в личный кабинет
    }
};

document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;

    await authUser(email, password);
});

async function authUser(email, password) {
    try {
        let response = await fetch(`https://${urlAddress}/api/authentication_token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        let result = await response.json();

        if (!response.ok) {
            console.error('Ошибка:', result);
            alert('Пароль или почта неправильные');
            return;
        }

        localStorage.setItem('token', result.token);
        localStorage.setItem('email', email);   // Сохраняем email
        localStorage.setItem('password', password); // Сохраняем пароль

        console.log('Успешный вход!', result);

        window.location.href = 'account.html';
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сети, либо серверная ошибка. Попробуйте позже.');
    }
}