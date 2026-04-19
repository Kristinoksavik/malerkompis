"""
app/chat.py — Malerkompis Chat
Håndterer API-kall til Claude og chat-logikk.
Portert fra gammel app.py — utvid herfra.
"""

from flask import Blueprint, request, jsonify, session
from app.auth import login_required
import os
import anthropic

chat_bp = Blueprint("chat", __name__)

# --- Systemmelding for Malerkompis ---
# TODO: Legg inn kunnskap fra Drive-dokumentene her (Brusho, Jordfarger, Akrylmerker, Fargeharmoni, Fargemiksing)
SYSTEM_PROMPT = """
Du er Malerkompis, en hjelpsom assistent for malere og kunstnere.
Du hjelper med fargeblanding, fargeharmoni, teknikker og materialer.
Svar på norsk med mindre brukeren skriver på engelsk.
"""

# Gratis spørsmål per session (for ikke-innloggede eller gratisbrukere)
FREE_QUESTIONS = 3


@chat_bp.route("/api/chat", methods=["POST"])
@login_required
def chat():
    """
    Tar imot POST med JSON: { "messages": [...], "language": "no"|"en" }
    Returnerer JSON: { "reply": "..." }

    messages-formatet følger Anthropic API: [{ "role": "user"|"assistant", "content": "..." }]
    """
    data = request.get_json()
    messages = data.get("messages", [])
    language = data.get("language", "no")

    if not messages:
        return jsonify({"error": "Ingen meldinger"}), 400

    # Velg systemmelding basert på språk
    # TODO: Legg til engelsk versjon av systemprompten
    system = SYSTEM_PROMPT

    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=system,
            messages=messages
        )
        reply = response.content[0].text
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/api/chat/free", methods=["POST"])
def chat_free():
    """
    Gratisversjon — maks FREE_QUESTIONS spørsmål per session.
    Samme format som /api/chat.
    TODO: Koble til betalingsløsning eller registrering for å fjerne grensen.
    """
    count = session.get("free_count", 0)

    if count >= FREE_QUESTIONS:
        return jsonify({
            "error": "free_limit",
            "message": "Du har brukt dine 3 gratis spørsmål. Logg inn for å fortsette."
        }), 403

    # Kall vanlig chat-logikk
    session["free_count"] = count + 1
    return chat()
