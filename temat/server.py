
"""
Vendose brenda temat/ dhe ekzekuto me FILLO.bat
"""

import http.server
import subprocess
import sys
import os
import json
import sqlite3
import hashlib

FOLDER = os.path.dirname(os.path.abspath(__file__))
PORT   = 8000
DB     = os.path.join(FOLDER, "perdoruesit.db")


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


def regjistro_perdoruesin(emri, fjalkalimi):
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO perdoruesit (emri, fjalkalimi) VALUES (?, ?)",
            (emri, hash_fjalk(fjalkalimi))
        )
        con.commit()
        con.close()
        return {"ok": True}
    except sqlite3.IntegrityError:
        return {"ok": False, "gabim": "Ky emer perdoruesi ekziston tashme!"}
    except Exception as e:
        return {"ok": False, "gabim": str(e)}


def kontrollo_login(emri, fjalkalimi):
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute(
            "SELECT id FROM perdoruesit WHERE emri=? AND fjalkalimi=?",
            (emri, hash_fjalk(fjalkalimi))
        )
        perdoruesi = cur.fetchone()
        con.close()
        if perdoruesi:
            return {"ok": True}
        else:
            return {"ok": False, "gabim": "Emri ose fjalkalimi eshte i gabuar!"}
    except Exception as e:
        return {"ok": False, "gabim": str(e)}


# ── Handler kryesor ───────────────────────────────────────────────────────
class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FOLDER, **kwargs)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        try:
            data = json.loads(body)
        except:
            data = {}

        if self.path == "/regjistrohu":
            emri       = data.get("emri", "").strip()
            fjalkalimi = data.get("fjalkalimi", "")
            if not emri or not fjalkalimi:
                resp = {"ok": False, "gabim": "Ploteso te gjitha fushat!"}
            else:
                resp = regjistro_perdoruesin(emri, fjalkalimi)
            self._dergoje(resp)

        elif self.path == "/login":
            emri       = data.get("emri", "").strip()
            fjalkalimi = data.get("fjalkalimi", "")
            if not emri or not fjalkalimi:
                resp = {"ok": False, "gabim": "Ploteso te gjitha fushat!"}
            else:
                resp = kontrollo_login(emri, fjalkalimi)
            self._dergoje(resp)

        elif self.path == "/run-snake":
            snake_path = os.path.join(FOLDER, "snake.py")
            if not os.path.exists(snake_path):
                self._dergoje({"ok": False, "gabim": "snake.py nuk u gjet!"})
            else:
                try:
                    subprocess.Popen([sys.executable, snake_path])
                    self._dergoje({"ok": True})
                except Exception as e:
                    self._dergoje({"ok": False, "gabim": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _dergoje(self, obj):
        resp = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.end_headers()
        self.wfile.write(resp)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, fmt, *args):
        path = args[0] if args else ""
        if any(x in path for x in ["/login", "/regjistrohu", "/run-snake"]):
            print(f"  [{args[1]}] {path}")


if __name__ == "__main__":
    init_db()
    os.chdir(FOLDER)
    print()
    print("=" * 54)
    print("  Python Academy — Server  ✅ Duke u nisur...")
    print(f"  Databaza: {DB}")
    print(f"  Hap: http://localhost:{PORT}/registry.html")
    print("  (CTRL+C per te ndalur)")
    print("=" * 54)
    print()
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()