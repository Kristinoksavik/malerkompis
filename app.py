"""
app.py — Malerkompis
Alt i én fil for enkel deploy på Render.
"""

from flask import Flask, request, session, redirect, jsonify, render_template_string
from functools import wraps
import os
import anthropic

app = Flask(__name__)

# ── Konfigurasjon ──────────────────────────────────────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-bytt-meg")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
APP_PASSWORD   = os.environ.get("APP_PASSWORD", "maler")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── System-prompt for Malerkompis chat ────────────────────────────────────────
SYSTEM_PROMPT_NO = """
Du er Malerkompis, en hjelpsom assistent for malere og kunstnere laget av Creative Business Academy.
Du hjelper med fargeblanding, fargeharmoni, teknikker og materialer — spesielt akryl, Brusho krystallfarger og jordfarger.
Svar alltid på norsk med mindre brukeren skriver på engelsk.
Hold svarene korte og praktiske.
"""

SYSTEM_PROMPT_EN = """
You are Paintbuddy, a helpful assistant for painters and artists made by Creative Business Academy.
You help with colour mixing, colour harmony, techniques and materials — especially acrylics, Brusho crystal colours and earth pigments.
Answer in English. Keep answers short and practical.
"""

# ── Dekoratorer ────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

# ── Innlogging ─────────────────────────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    password = data.get("password", "")

    if password == ADMIN_PASSWORD:
        session["logged_in"] = True
        session["is_admin"] = True
        return jsonify({"success": True})
    elif password == APP_PASSWORD:
        session["logged_in"] = True
        session["is_admin"] = False
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Feil passord"}), 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ── Status (brukes av frontend) ────────────────────────────────────────────────
@app.route("/api/status")
def status():
    return jsonify({
        "logged_in": bool(session.get("logged_in")),
        "is_admin": bool(session.get("is_admin"))
    })

# ── Forsiden ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return f.read()

# ── Chat API ───────────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json() or {}
    messages = data.get("messages", [])
    language = data.get("language", "no")

    if not messages:
        return jsonify({"error": "Ingen meldinger"}), 400

    system = SYSTEM_PROMPT_EN if language == "en" else SYSTEM_PROMPT_NO

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=messages
        )
        return jsonify({"reply": response.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Admin ──────────────────────────────────────────────────────────────────────
@app.route("/admin")
@admin_required
def admin():
    return render_template_string("""
<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<title>Admin — Malerkompis</title>
<style>
  body { font-family: system-ui, sans-serif; background: #f5f5f3; color: #1a1a1a;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; }
  .card { background: white; border-radius: 16px; padding: 2.5rem; max-width: 400px;
          width: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
  h1 { font-size: 22px; margin-bottom: 0.5rem; }
  p { color: #888; font-size: 14px; margin-bottom: 1.5rem; }
  a { display: inline-block; padding: 10px 24px; background: #1a1a1a; color: white;
      border-radius: 8px; text-decoration: none; font-size: 14px; }
</style>
</head>
<body>
  <div class="card">
    <h1>🎨 Admin</h1>
    <p>Malerkompis admin-panel</p>
    <p style="font-size:13px; color:#aaa;">Mer funksjonalitet kommer her.</p>
    <a href="/logout">Logg ut</a>
  </div>
</body>
</html>
""")

# ── Start ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False)
