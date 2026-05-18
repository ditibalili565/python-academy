"""
server.py - Python Academy
Databaza: Neon PostgreSQL (cloud)
"""

import http.server
import subprocess
import sys
import os
import json
import hashlib
import psycopg2
from urllib.parse import urlparse

FOLDER = os.path.dirname(os.path.abspath(__file__))
PORT   = int(os.environ.get("PORT", 8000))

# ── VENDOS KETU CONNECTION STRING-UN TEND ────────────────────────────────
CONNECTION_STRING = "postgresql://neondb_owner:npg_poHsSGg04Iqv@ep-solitary-wildflower-abgy5pem.eu-west-2.aws.neon.tech/neondb?sslmode=require"
# ─────────────────────────────────────────────────────────────────────────


def get_conn():
    return psycopg2.connect(CONNECTION_STRING, sslmode="require")


# ── Krijo tabelen nese nuk ekziston ──────────────────────────────────────
def init_db():
    try:
        con = get_conn()
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS perdoruesit (
                id         SERIAL PRIMARY KEY,
                emri       TEXT    UNIQUE NOT NULL,
                fjalkalimi TEXT    NOT NULL,
                data_reg   TIMESTAMP DEFAULT NOW()
            )
        """)
        con.commit()
        cur.close()
        con.close()
        print("  Databaza u lidh me sukses! ✅")
    except Exception as e:
        print(f"  GABIM me databazën: {e}")
        sys.exit(1)


def hash_fjalk(fjalkalimi):
    return hashlib.sha256(fjalkalimi.encode()).hexdigest()


def regjistro_perdoruesin(emri, fjalkalimi):
    try:
        con = get_conn()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO perdoruesit (emri, fjalkalimi) VALUES (%s, %s)",
            (emri, hash_fjalk(fjalkalimi))
        )
        con.commit()
        cur.close()
        con.close()
        return {"ok": True}
    except psycopg2.errors.UniqueViolation:
        return {"ok": False, "gabim": "Ky emer perdoruesi ekziston tashme!"}
    except Exception as e:
        return {"ok": False, "gabim": str(e)}


def kontrollo_login(emri, fjalkalimi):
    try:
        con = get_conn()
        cur = con.cursor()
        cur.execute(
            "SELECT id FROM perdoruesit WHERE emri=%s AND fjalkalimi=%s",
            (emri, hash_fjalk(fjalkalimi))
        )
        perdoruesi = cur.fetchone()
        cur.close()
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
        pass


if __name__ == "__main__":
    init_db()
    os.chdir(FOLDER)
    print()
    print("=" * 54)
    print("  Python Academy — Server  ✅ Duke u nisur...")
    print(f"  Databaza: Neon PostgreSQL (cloud)")
    print(f"  Hap: http://localhost:{PORT}/registry.html")
    print("  (CTRL+C per te ndalur)")
    print("=" * 54)
    print()
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()


def do_GET(self):
    if self.path == "/" or self.path == "":
        self.send_response(302)
        self.send_header("Location", "/registry.html")
        self._cors()
        self.end_headers()
    else:
        super().do_GET()