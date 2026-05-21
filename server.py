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
from urllib.parse import urlparse, parse_qs

FOLDER = os.path.dirname(os.path.abspath(__file__))
PORT   = int(os.environ.get("PORT", 8000))

CONNECTION_STRING = "postgresql://neondb_owner:npg_poHsSGg04Iqv@ep-solitary-wildflower-abgy5pem.eu-west-2.aws.neon.tech/neondb?sslmode=require"


def get_conn():
    return psycopg2.connect(CONNECTION_STRING, sslmode="require")


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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS snake_pike (
                id           SERIAL PRIMARY KEY,
                perdorues_id INTEGER NOT NULL,
                pike         INTEGER NOT NULL,
                data         TIMESTAMP DEFAULT NOW()
            )
        """)
        con.commit()
        cur.close(); con.close()
        print("  Databaza u lidh me sukses! ✅")
    except Exception as e:
        print(f"  GABIM me databazën: {e}")
        sys.exit(1)


def hash_fjalk(fjalkalimi):
    return hashlib.sha256(fjalkalimi.encode()).hexdigest()


def regjistro_perdoruesin(emri, fjalkalimi):
    try:
        con = get_conn(); cur = con.cursor()
        cur.execute("INSERT INTO perdoruesit (emri, fjalkalimi) VALUES (%s, %s)",
                    (emri, hash_fjalk(fjalkalimi)))
        con.commit(); cur.close(); con.close()
        return {"ok": True}
    except psycopg2.errors.UniqueViolation:
        return {"ok": False, "gabim": "Ky emer perdoruesi ekziston tashme!"}
    except Exception as e:
        return {"ok": False, "gabim": str(e)}


def kontrollo_login(emri, fjalkalimi):
    try:
        con = get_conn(); cur = con.cursor()
        cur.execute("SELECT id FROM perdoruesit WHERE emri=%s AND fjalkalimi=%s",
                    (emri, hash_fjalk(fjalkalimi)))
        row = cur.fetchone(); cur.close(); con.close()
        if row:
            return {"ok": True}
        return {"ok": False, "gabim": "Emri ose fjalkalimi eshte i gabuar!"}
    except Exception as e:
        return {"ok": False, "gabim": str(e)}


def ruaj_pike_snake(emri, pike):
    try:
        con = get_conn(); cur = con.cursor()
        cur.execute("SELECT id FROM perdoruesit WHERE emri=%s", (emri,))
        row = cur.fetchone()
        if not row:
            cur.close(); con.close()
            return {"ok": False, "gabim": "Perdoruesi nuk u gjet!"}
        cur.execute("INSERT INTO snake_pike (perdorues_id, pike) VALUES (%s, %s)",
                    (row[0], pike))
        con.commit(); cur.close(); con.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "gabim": str(e)}


def merr_piket_snake(emri):
    try:
        con = get_conn(); cur = con.cursor()
        cur.execute("SELECT id FROM perdoruesit WHERE emri=%s", (emri,))
        row = cur.fetchone()
        if not row:
            cur.close(); con.close()
            return {"ok": False, "gabim": "Perdoruesi nuk u gjet!"}
        pid = row[0]
        cur.execute("SELECT MAX(pike) FROM snake_pike WHERE perdorues_id=%s", (pid,))
        rekordi = cur.fetchone()[0] or 0
        cur.execute("""SELECT pike, data FROM snake_pike
                       WHERE perdorues_id=%s ORDER BY data DESC LIMIT 10""", (pid,))
        lojrat = cur.fetchall()
        cur.close(); con.close()
        return {
            "ok": True,
            "rekordi": rekordi,
            "lojrat": [{"pike": r[0], "data": str(r[1])} for r in lojrat]
        }
    except Exception as e:
        return {"ok": False, "gabim": str(e)}


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
            emri = data.get("emri", "").strip()
            fj   = data.get("fjalkalimi", "")
            resp = regjistro_perdoruesin(emri, fj) if emri and fj else \
                   {"ok": False, "gabim": "Ploteso te gjitha fushat!"}
            self._dergoje(resp)

        elif self.path == "/login":
            emri = data.get("emri", "").strip()
            fj   = data.get("fjalkalimi", "")
            resp = kontrollo_login(emri, fj) if emri and fj else \
                   {"ok": False, "gabim": "Ploteso te gjitha fushat!"}
            self._dergoje(resp)

        elif self.path == "/ruaj-snake":
            emri = data.get("emri", "").strip()
            pike = data.get("pike", 0)
            resp = ruaj_pike_snake(emri, pike) if emri else \
                   {"ok": False, "gabim": "Emri mungon!"}
            self._dergoje(resp)

        elif self.path == "/run-snake":
            # ── NDRYSHIMI: merr emrin dhe kalo si argument ──
            emri       = data.get("emri", "").strip()
            snake_path = os.path.join(FOLDER, "snake.py")
            if not os.path.exists(snake_path):
                self._dergoje({"ok": False, "gabim": "snake.py nuk u gjet!"})
            else:
                try:
                    args = [sys.executable, snake_path]
                    if emri:
                        args.append(emri)
                    subprocess.Popen(args)
                    self._dergoje({"ok": True})
                except Exception as e:
                    self._dergoje({"ok": False, "gabim": str(e)})
            # ────────────────────────────────────────────────

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(302)
            self.send_header("Location", "/index.html")
            self._cors()
            self.end_headers()
        elif self.path.startswith("/merr-piket"):
            params = parse_qs(urlparse(self.path).query)
            emri   = params.get("emri", [""])[0].strip()
            resp   = merr_piket_snake(emri) if emri else \
                     {"ok": False, "gabim": "Emri mungon!"}
            self._dergoje(resp)
        else:
            super().do_GET()

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