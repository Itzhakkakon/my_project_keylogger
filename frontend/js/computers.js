const API_URL = 'http://localhost:5000/api';

function checkAuth() {
    if (!sessionStorage.getItem('isLoggedIn')) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function logout() {
    sessionStorage.removeItem('isLoggedIn');
    window.location.href = 'login.html';
}

async function fetchComputers() {
    try {
        const response = await fetch(`${API_URL}/computers`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const computers = await response.json();
        displayComputers(computers);
    } catch (error) {
        console.error('Error fetching computers:', error);
        document.getElementById('computersGrid').innerHTML = 
            `<div class="alert alert-danger">שגיאה בטעינת הנתונים: ${error.message}</div>`;
    }
}

function displayComputers(computers) {
    const grid = document.getElementById('computersGrid');
    
    if (!computers.length) {
        grid.innerHTML = '<div class="alert alert-info">לא נמצאו מחשבים מנוטרים</div>';
        return;
    }

    grid.innerHTML = computers.map(computer => `
        <div class="computer-card" onclick="openComputerLogs('${computer.name}')">
            <div class="computer-icon">
                <i class="fas fa-desktop"></i>
            </div>
            <div class="computer-info">
                <h3>${computer.name}</h3>
                <p>נרשם לאחרונה: ${formatDate(computer.lastSeen)}</p>
                <p>רשומות: ${computer.logsCount}</p>
            </div>
        </div>
    `).join('');
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('he-IL');
}

function openComputerLogs(computerName) {
    sessionStorage.setItem('selectedComputer', computerName);
    window.location.href = 'index.html';
}

document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth()) return;
    fetchComputers();
    setInterval(fetchComputers, 30000); // רענון כל 30 שניות
});
