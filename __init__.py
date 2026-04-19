"""
app/__init__.py — Application Factory
Oppretter og konfigurerer Flask-appen.
Registrerer alle blueprints her.
"""

from flask import Flask
import os


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    # --- Konfigurasjon ---
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-bytt-meg")
    app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "admin")
    app.config["APP_PASSWORD"] = os.environ.get("APP_PASSWORD", "maler")  # Brukerpassord for innlogging

    # --- Registrer blueprints ---
    from app.auth import auth_bp
    from app.routes import routes_bp
    from app.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(chat_bp)

    return app
