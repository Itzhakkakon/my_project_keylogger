# my_project_keylogger
dfgbn
אסביר את השלבים להפעלת המערכת בצורה מסודרת:

שלב 1: התקנת ספריות Python נדרשות
פתח Command Prompt והרץ:
/////////   pip install flask flask-cors pynput psutil pywin32
שלב 2: הכנת התיקיות
וודא שקיימת תיקיית data בנתיב:
שלב 3: הפעלת השרת (Flask)
פתח Command Prompt
נווט לתיקיית agent:
//////////  cd C:\Users\Itzhak\Desktop\my project keyloger\agent
הפעל את השרת:
//////////    python server.py
השרת אמור לרוץ על http://localhost:5000

שלב 4: הפעלת שרת ה-Frontend
פתח Command Prompt חדש
נווט לתיקיית frontend:
//////////////   cd C:\Users\Itzhak\Desktop\my project keyloger\frontend
הפעל את שרת ה-frontend:
//////////////   python serve.py
הממשק יהיה זמין ב-http://localhost:8000

שלב 5: הפעלת הקיילוגר
פתח Command Prompt חדש
נווט לתיקיית agent:
////////////     cd C:\Users\Itzhak\Desktop\my project keyloger\agent
הפעל את הקיילוגר:
///////////      python keylogger.py
שלב 6: גישה למערכת
פתח דפדפן
גש ל-http://localhost:8000
התחבר עם:
שם משתמש: admin
סיסמה: admin123