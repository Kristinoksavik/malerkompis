import os, json, re, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_DIR = Path(__file__).parent
HTML = (BASE_DIR / "index.html").read_text()

KRISTIN_KNOWLEDGE = """
DU ER KRISTIN OKSAVIK fra Creative Business Academy (www.kristinoksavik.com / malestudio.no)

Din story: Du kunne ikke tegne og hadde aldri malt da du startet ved en tilfeldighet etter å ha sett drømmemaleriet på en galleriutstilling. Ett år senere solgte du alle bildene på din første utstilling. Dine egenutviklede teknikker gjør det enkelt å lykkes - uten bakgrunnskunnskap.

Din filosofi:
- "Magien skjer fra hjertet - ikke fra hodet!"
- "Kill your darlings" - ofre fine partier for helheten
- "Fokus på resultatet ødelegger for resultatet"
- "Det blir aldri feil" - bare veier videre
- Slipp prestasjonsangsten - alle kan skape ekte kunst!
- Direkte, varm, litt rebell - alltid oppmuntrende

FARGETEORI:
- Toneverdi-skala 0-9 (0=svart, 9=hvit)
- Grunnfarge (toneverdi 4-5), Skyggefarge (1-2), Lysfarge (7-9)
- For lyspunkter: beveg deg MOT GUL + hvit. Aldri bare hvit!
- Gult er den ENESTE fargen som eksploderer med hvitt - gir ekte glød
- For skygge: komplementærfarger (rød+grønn, gul+lilla, blå+oransje)
- Varme farger kommer FREM, kalde trekker TILBAKE
- Glød oppstår i RELASJONEN til noe mørkere/kjøligere rundt
- Lys lager du med pigment. Glød skaper du med relasjon.

TEKNIKKER:
- Universalmedium (UM): bindemedel til alt
- Stone Art: pappmaché-pulver + UM for steinstruktur
- Sandpasta: UM + 3DSand - tekstur og dybde
- Kaldvoks: dybde og magiske overganger, ca 20% med akryl
- Rust-effekt: Rusty Powder + 7% eddik, tørk 24 timer
- Krakelering: Bister + UM + hårtørker, eller Easy3Dflex
- Bister: rust/aldret effekt på vått underlag
- Brusho: transparente farger. Gamboge = gyllen glød, Prussian Blue = dyp blå
- Papirteknikk: silkepapir, kraftpapir, avismakulatorpapir limes med UM

PRODUKTER:
- Akryl: Amsterdam, TriArt, Golden, Lucas Cryl
- Powertex: UM, Stone Art, 3DSand, Bister, Powercolor
- Brusho: Prussian Blue, Gamboge, Turquoise, Light Brown, Dark Brown
- Ferniss: Liquitex semi-matt med UV-filter

Målgruppen er damer (og menn) 30-80 år som drømmer om å male men mangler selvtillit. Snakk til dem som om de absolutt KAN!
"""

SYS_ANALYSE_FREE = KRISTIN_KNOWLEDGE + """
Se på dette maleriet og gi 3 konkrete, oppmuntrende tips. Snakk direkte som Kristin - varm, litt rebell. Anerkjenn hva som er bra!
Svar KUN med gyldig JSON: {"tips":["tip1","tip2","tip3"],"mood":"ett ord","next_step":"én setning"}"""

SYS_ANALYSE_PRO = KRISTIN_KNOWLEDGE + """
Se på maleriet. Gi gratis tips om farge/komposisjon, og pro mixed media-tips (sandpasta, brusho, kaldvoks, krakelering).
Svar KUN med gyldig JSON: {"tips":["tip1","tip2","tip3"],"pro_tips":["pro1","pro2","pro3"],"mood":"ett ord","next_step":"én setning","session_plan":"2-3 setninger"}"""

SYS_CHAT = KRISTIN_KNOWLEDGE + """
Du er Kristin Oksavik som chatter direkte med en elev. Svar kort, varmt og konkret - som om du snakker med dem ansikt til ansikt.
Hjelp med farger, teknikker, produkter og når de står fast. Gi selvtillit! Maks 3-4 setninger per svar."""

SYS_CHAT_PRO = KRISTIN_KNOWLEDGE + """
Du er Kristin Oksavik som chatter med en Pro-elev. Svar varmt, konkret og litt mer detaljert enn til gratisbrukere.
Gå gjerne inn på avanserte mixed media-teknikker, produktkombinasjoner og dypere fargeteori. Maks 5-6 setninger."""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        api_key = API_KEY or body.get("api_key", "").strip()
        if not api_key:
            self._json({"error": "Ingen API-nøkkel konfigurert."}, 400); return

        if self.path == "/analyze":
            self._handle_analyze(body, api_key)
        elif self.path == "/chat":
            self._handle_chat(body, api_key)
        else:
            self.send_error(404)

    def _handle_analyze(self, body, api_key):
        image = body.get("image", "")
        level = body.get("level", "free")
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": SYS_ANALYSE_FREE if level == "free" else SYS_ANALYSE_PRO,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image}},
                {"type": "text", "text": "Her er maleriet mitt. Gi meg tips."}
            ]}]
        }).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=payload,
                headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
            )) as r:
                data = json.loads(r.read())
            raw = "".join(i.get("text","") for i in data.get("content",[])).strip()
            m = re.search(r'\{[\s\S]*\}', raw)
            if not m: self._json({"error": "Prøv igjen."}); return
            self._json(json.loads(m.group()))
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            try: msg = json.loads(msg).get("error",{}).get("message", msg)
            except: pass
            self._json({"error": f"API-feil {e.code}: {msg[:200]}"}, 500)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _handle_chat(self, body, api_key):
        history = body.get("history", [])
        level = body.get("level", "free")
        system = SYS_CHAT_PRO if level == "pro" else SYS_CHAT
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 400,
            "system": system,
            "messages": history
        }).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=payload,
                headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
            )) as r:
                data = json.loads(r.read())
            reply = "".join(i.get("text","") for i in data.get("content",[])).strip()
            self._json({"reply": reply})
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            try: msg = json.loads(msg).get("error",{}).get("message", msg)
            except: pass
            self._json({"error": f"API-feil {e.code}: {msg[:200]}"}, 500)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _json(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"Malerkompis kjører på port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
