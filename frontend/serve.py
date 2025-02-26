from flask import Flask, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("[LOG] Frontend server running on http://localhost:8000")
    print("[LOG] Press Ctrl+C to stop")
    app.run(port=8000, debug=True)
