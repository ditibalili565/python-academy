import os
import json
import sqlite3
import hashlib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

FOLDER = os.path.dirname(os.path.abspath(__file__))
DB     = os.path.join(FOLDER, "perdoruesit.db")

app = Flask(__name__, static_folder=FOLDER)
CORS(app)

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS perdoruesit (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            emri       TEXT    UNIQUE NOT NULL,
            fjalkalimi TEXT    NOT NULL,
            data_reg   TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)
    con.commit()
    con.close()

def hash_fjalk(fjalkalimi):
    return hashlib.sha256(fjalkalimi.encode()).hexdigest()

@app.route('/regjistrohu', methods=['POST'])
def regjistrohu():
    data = request.get_json() or {}
    emri = data.get("emri", "").strip()
    fjalkalimi = data.get("fjalkalimi", "")
    
    if not emri or not fjalkalimi:
        return jsonify({"ok": False, "gabim": "Ploteso te gjitha fushat!"})
        
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("INSERT INTO perdoruesit (emri, fjalkalimi) VALUES (?, ?)", (emri, hash_fjalk(fjalkalimi)))
        con.commit()
        con.close()
        return jsonify({"ok": True})
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "gabim": "Ky emer perdoruesi ekziston tashme!"})
    except Exception as e:
        return jsonify({"ok": False, "gabim": str(e)})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    emri = data.get("emri", "").strip()
    fjalkalimi = data.get("fjalkalimi", "")
    
    if not emri or not fjalkalimi:
        return jsonify({"ok": False, "gabim": "Ploteso te gjitha fushat!"})
        
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT id FROM perdoruesit WHERE emri=? AND fjalkalimi=?", (emri, hash_fjalk(fjalkalimi)))
        perdoruesi = cur.fetchone()
        con.close()
        if perdoruesi:
            return jsonify({"ok": True})
        return jsonify({"ok": False, "gabim": "Emri ose fjalkalimi eshte i gabuar!"})
    except Exception as e:
        return jsonify({"ok": False, "gabim": str(e)})

@app.route('/')
def home():
    return send_from_directory(FOLDER, 'registry.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FOLDER, path)

init_db()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
