"""
app.py — Inngangsport
Starter Flask-appen. Ingenting annet skjer her.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
