document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // כאן אתה יכול להוסיף את פרטי ההתחברות הקבועים
    const validUsername = 'admin';
    const validPassword = 'admin123';
    
    if (username === validUsername && password === validPassword) {
        // שמירת מצב התחברות
        sessionStorage.setItem('isLoggedIn', 'true');
        // שינוי הניתוב לדף המחשבים
        window.location.href = 'computers.html';
    } else {
        document.getElementById('errorMessage').textContent = 'שם משתמש או סיסמה שגויים';
    }
});
