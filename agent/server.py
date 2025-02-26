from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # מאפשר CORS

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

@app.route('/')
def home():
    return "Server is running!"

@app.route("/api/upload", methods=["POST"])
def upload_data():
    """ מקבל נתונים מה-Manager ושומר אותם לקובץ """
    data = request.get_json()
    if not data or "machine" not in data or "data" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    machine_name = data["machine"]
    encrypted_data = data["data"]

    machine_folder = os.path.join(DATA_FOLDER, machine_name)
    if not os.path.exists(machine_folder):
        os.makedirs(machine_folder)

    filename = os.path.join(machine_folder, "log.json")

    file_data = []
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                file_data = json.load(f)
            except json.JSONDecodeError:
                file_data = []

    file_data.append({"encrypted": encrypted_data})

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=4, ensure_ascii=False)

    print(f"[LOG] Data saved for {machine_name}.")
    return jsonify({"status": "success", "file": filename}), 200

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """ מחזיר את כל הלוגים המפוענחים """
    from encryptor import xor_decrypt
    all_logs = []
    
    try:
        if not os.path.exists(DATA_FOLDER):
            print(f"[DEBUG] Data folder not found: {DATA_FOLDER}")
            return jsonify([])

        for machine_folder in os.listdir(DATA_FOLDER):
            # תיקון: שימוש ב-machine_folder במקום machine_name
            log_file = os.path.join(DATA_FOLDER, machine_folder, "log.json")
            print(f"[DEBUG] Checking log file: {log_file}")
            
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    try:
                        encrypted_logs = json.load(f)
                        for entry in encrypted_logs:
                            try:
                                decrypted_data = xor_decrypt(entry["encrypted"])
                                log_data = json.loads(decrypted_data)
                                log_data["machine"] = machine_folder
                                all_logs.append(log_data)
                            except Exception as e:
                                print(f"[ERROR] Failed to decrypt entry: {e}")
                    except json.JSONDecodeError as e:
                        print(f"[ERROR] Failed to parse JSON from {log_file}: {e}")

    except Exception as e:
        print(f"[ERROR] Error in get_logs: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify(all_logs)

@app.route("/api/computers", methods=["GET"])
def get_computers():
    """מחזיר רשימת מחשבים מנוטרים"""
    from encryptor import xor_decrypt
    computers = []
    try:
        for computer_name in os.listdir(DATA_FOLDER):
            log_file = os.path.join(DATA_FOLDER, computer_name, "log.json")
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    encrypted_logs = json.load(f)
                    last_seen = None
                    try:
                        # מפענח את הרשומה האחרונה לקבלת timestamp
                        if encrypted_logs:
                            last_encrypted = encrypted_logs[-1]["encrypted"]
                            last_decrypted = json.loads(xor_decrypt(last_encrypted))
                            last_seen = last_decrypted.get("timestamp")
                    except Exception as e:
                        print(f"[ERROR] Failed to decrypt last log: {e}")
                    
                    computers.append({
                        "name": computer_name,
                        "lastSeen": last_seen,
                        "logsCount": len(encrypted_logs)
                    })
    except Exception as e:
        print(f"[ERROR] Error in get_computers: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify(computers)

@app.route("/api/logs/<computer>", methods=["GET"])
def get_computer_logs(computer):
    """מחזיר את הלוגים של מחשב ספציפי"""
    from encryptor import xor_decrypt
    all_logs = []
    
    try:
        log_file = os.path.join(DATA_FOLDER, computer, "log.json")
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                try:
                    encrypted_logs = json.load(f)
                    for entry in encrypted_logs:
                        try:
                            decrypted_data = xor_decrypt(entry["encrypted"])
                            log_data = json.loads(decrypted_data)
                            log_data["machine"] = computer
                            all_logs.append(log_data)
                        except Exception as e:
                            print(f"[ERROR] Failed to decrypt entry: {e}")
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse JSON from {log_file}: {e}")

    except Exception as e:
        print(f"[ERROR] Error in get_computer_logs: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify(all_logs)

if __name__ == "__main__":
    print("[LOG] Server started on http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0")


