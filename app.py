import os, json, re, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "sett_passord_her")
BASE_DIR = Path(__file__).parent
HTML = (BASE_DIR / "index.html").read_text()
LOG_FILE = BASE_DIR / "chat_log.jsonl"

KRISTIN_KNOWLEDGE = """
DU ER KRISTIN OKSAVIK fra Creative Business Academy (www.kristinoksavik.com / malestudio.no)

Svar KUN på spørsmål om maling, farger, teknikker, produkter og kreativitet. Hvis noen spør om noe helt annet, si vennlig at du kun hjelper med maling og kunst.

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

TEKNIKKER OG PRODUKTER:
- Universalmedium (UM): bindemedel til alt
- Stone Art: pappmaché-pulver + UM for steinstruktur (gnuggteknikk)
- Sandpasta: UM + 3DSand - tekstur og dybde
- Kaldvoks: dybde og magiske overganger, ca 20% med akryl
- Rust-effekt: Rusty Powder + 7% eddik, tørk 24 timer
- Krakelering: Bister + UM + hårtørker, eller Easy3Dflex
- Bister: rust/aldret effekt på vått underlag
- Brusho: transparente akvarellfarger i pulverform. Bland 1 teskje Brusho-pulver med 1 dl vann (gjerne lunkent), bland godt til krystallene løser seg opp. Bruk i sprayflaske. Jobb vått-i-vått med struktur eller binder. Har INGEN bindemiddel - kan vaskes bort hvis lagt på tørt underlag!
- Papirteknikk: silkepapir, kraftpapir, avismakulatorpapir limes med UM
- Akryl: Amsterdam, TriArt, Golden, Lucas Cryl
- Powertex: UM, Stone Art, 3DSand, Bister, Powercolor
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
Du er Kristin Oksavik som chatter med en elev. Svar kort, varmt og konkret. Maks 3-4 setninger.
Hjelp kun med maling, farger, teknikker og kreativitet."""

SYS_CHAT_PRO = KRISTIN_KNOWLEDGE + """
Du er Kristin Oksavik som chatter med en Pro-elev. Svar varmt og mer detaljert.
Gå gjerne inn på avanserte mixed media-teknikker. Maks 5-6 setninger.
Hjelp kun med maling, farger, teknikker og kreativitet."""

ADMIN_HTML = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin – Malerkompis</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, sans-serif; background: #f5f4f0; padding: 2rem 1rem; }
  .wrap { max-width: 700px; margin: 0 auto; }
  h1 { font-size: 20px; font-weight: 600; margin-bottom: 1.5rem; color: #1a1a1a; }
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 1.5rem; }
  .stat { background: #fff; border-radius: 10px; padding: 1rem; text-align: center; border: 0.5px solid #e0dfd8; }
  .stat-num { font-size: 28px; font-weight: 600; color: #7F77DD; }
  .stat-label { font-size: 12px; color: #888; margin-top: 4px; }
  .log-item { background: #fff; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 10px; border: 0.5px solid #e0dfd8; }
  .log-meta { font-size: 11px; color: #aaa; margin-bottom: 6px; }
  .log-q { font-size: 14px; color: #1a1a1a; font-weight: 500; margin-bottom: 4px; }
  .log-a { font-size: 13px; color: #555; line-height: 1.6; }
  .badge { display: inline-block; font-size: 10px; padding: 2px 7px; border-radius: 6px; font-weight: 500; margin-left: 6px; }
  .pro { background: #EEEDFE; color: #3C3489; }
  .free { background: #EAF3DE; color: #3B6D11; }
  .login { max-width: 320px; margin: 4rem auto; background: #fff; border-radius: 12px; padding: 2rem; border: 0.5px solid #e0dfd8; text-align: center; }
  .login input { width: 100%; padding: 10px 14px; font-size: 14px; border: 0.5px solid #d0cfc8; border-radius: 8px; margin: 1rem 0; }
  .login button { width: 100%; padding: 11px; background: #7F77DD; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; }
  .empty { text-align: center; color: #888; padding: 3rem; font-size: 14px; }
</style>
</head>
<body>
<div class="wrap">
  <div id="login-screen" class="login">
    <div style="font-size:24px;margin-bottom:8px">🎨</div>
    <div style="font-size:16px;font-weight:600;margin-bottom:4px">Admin</div>
    <div style="font-size:13px;color:#888">Malerkompis</div>
    <input type="password" id="pw-input" placeholder="Passord" onkeydown="if(event.key==='Enter')login()" />
    <button onclick="login()">Logg inn</button>
    <div id="pw-error" style="font-size:12px;color:#791F1F;margin-top:8px"></div>
  </div>
  <div id="admin-screen" style="display:none">
    <h1>🎨 Malerkompis — Logg</h1>
    <div id="stats" class="stats"></div>
    <div id="log-list"></div>
  </div>
</div>
<script>
function login() {
  const pw = document.getElementById('pw-input').value;
  fetch('/admin/data', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pw }) })
    .then(r => r.json()).then(data => {
      if (data.error) { document.getElementById('pw-error').textContent = 'Feil passord'; return; }
      document.getElementById('login-screen').style.display = 'none';
      document.getElementById('admin-screen').style.display = 'block';
      renderData(data);
    });
}
function renderData(data) {
  const logs = data.logs || [];
  const total = logs.length;
  const pro = logs.filter(l => l.level === 'pro').length;
  const topics = {};
  logs.forEach(l => { const w = l.question.split(' ')[0].toLowerCase(); topics[w] = (topics[w]||0)+1; });
  document.getElementById('stats').innerHTML =
    '<div class="stat"><div class="stat-num">'+total+'</div><div class="stat-label">Totalt spørsmål</div></div>' +
    '<div class="stat"><div class="stat-num">'+pro+'</div><div class="stat-label">Pro-spørsmål</div></div>' +
    '<div class="stat"><div class="stat-num">'+(total-pro)+'</div><div class="stat-label">Gratis spørsmål</div></div>';
  if (!logs.length) { document.getElementById('log-list').innerHTML = '<div class="empty">Ingen spørsmål ennå</div>'; return; }
  document.getElementById('log-list').innerHTML = [...logs].reverse().map(l =>
    '<div class="log-item"><div class="log-meta">'+l.time+' <span class="badge '+(l.level==='pro'?'pro':'free')+'">'+(l.level==='pro'?'Pro':'Gratis')+'</span></div>' +
    '<div class="log-q">'+l.question+'</div><div class="log-a">'+l.answer+'</div></div>'
  ).join('');
}
</script>
</body>
</html>"""

def save_log(question, answer, level):
    entry = {"time": datetime.now().strftime("%d.%m.%Y %H:%M"), "question": question, "answer": answer, "level": level}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def read_log():
    if not LOG_FILE.exists(): return []
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try: logs.append(json.loads(line.strip()))
            except: pass
    return logs

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path == "/admin":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(ADMIN_HTML.encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        if self.path == "/admin/data":
            if body.get("password") != ADMIN_PASSWORD:
                self._json({"error": "Feil passord"}, 401); return
            self._json({"logs": read_log()}); return

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
            "model": "claude-sonnet-4-20250514", "max_tokens": 1000,
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
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _handle_chat(self, body, api_key):
        history = body.get("history", [])
        level = body.get("level", "free")
        system = SYS_CHAT_PRO if level == "pro" else SYS_CHAT
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514", "max_tokens": 400,
            "system": system, "messages": history
        }).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=payload,
                headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
            )) as r:
                data = json.loads(r.read())
            reply = "".join(i.get("text","") for i in data.get("content",[])).strip()
            question = history[-1]["content"] if history else ""
            save_log(question, reply, level)
            self._json({"reply": reply})
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"Malerkompis kjører på port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
