"""
app/auth.py — Autentisering
Håndterer innlogging, utlogging og session-sjekk.
Brukes både for vanlige brukere og admin.
"""

from flask import Blueprint, request, session, redirect, url_for, jsonify, current_app
from functools import wraps

auth_bp = Blueprint("auth", __name__)


# --- Dekoratorer for å beskytte ruter ---

def login_required(f):
    """Krever at brukeren er innlogget."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Krever at brukeren er innlogget som admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated


# --- Ruter ---

@auth_bp.route("/login", methods=["GET"])
def login_page():
    """Viser innloggingssiden."""
    # TODO: returner templates/login.html når den er laget
    return "<h1>Logg inn</h1>"  # Midlertidig placeholder


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Tar imot POST med JSON: { "password": "..." }
    Sjekker mot APP_PASSWORD (bruker) eller ADMIN_PASSWORD (admin).
    Returnerer JSON med success/error.
    """
    data = request.get_json()
    password = data.get("password", "")

    admin_pw = current_app.config["ADMIN_PASSWORD"]
    app_pw = current_app.config["APP_PASSWORD"]

    if password == admin_pw:
        session["logged_in"] = True
        session["is_admin"] = True
        return jsonify({"success": True, "redirect": "/admin"})
    elif password == app_pw:
        session["logged_in"] = True
        session["is_admin"] = False
        return jsonify({"success": True, "redirect": "/"})
    else:
        return jsonify({"success": False, "error": "Feil passord"}), 401


@auth_bp.route("/logout")
def logout():
    """Logger ut og sender til innloggingssiden."""
    session.clear()
    return redirect(url_for("auth.login_page"))
