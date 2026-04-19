"""
app/routes.py — Sideruter
"""
from flask import Blueprint, render_template, jsonify, session
from app.auth import login_required, admin_required

routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/")
@login_required
def index():
    return render_template("index.html")


@routes_bp.route("/api/status")
def status():
    """Brukes av frontend for å sjekke om man er logget inn."""
    return jsonify({
        "logged_in": bool(session.get("logged_in")),
        "is_admin": bool(session.get("is_admin"))
    })


@routes_bp.route("/admin")
@admin_required
def admin():
    return render_template("admin.html")
