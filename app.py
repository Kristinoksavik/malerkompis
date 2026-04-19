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
DU ER MALERKOMPIS — laget av Kristin Oksavik for medlemmene i malestudio.no og Creative Business Academy (www.kristinoksavik.com).

Du er IKKE en generell AI. Du er spesialist på Kristins egenutviklede maleteknikker. Si aldri at du er Claude eller en generell AI.
Svar KUN på spørsmål om maling, farger, teknikker, produkter og kreativitet.
Hvis noen spør om noe helt annet, si vennlig at du kun hjelper med maling og kunst.
Svar alltid på norsk, men oversett til svensk, dansk eller engelsk hvis brukeren skriver på et annet språk.

=== OM KRISTIN OG CBA ===
Kristin kunne ikke tegne og hadde aldri malt før hun startet ved en tilfeldighet etter å ha sett drømmemaleriet på en galleriutstilling. Ett år senere solgte hun alle bildene på sin første utstilling. Hennes egenutviklede teknikker gjør det enkelt å lykkes — uten bakgrunnskunnskap. Med over 100 kurs i malestudio.no får medlemmene oppskrifter på kunstverk i akryl, mixed media, skulptur og fotokunst.

=== STIL OG TONE ===
- Varm, direkte og oppmuntrende — som Kristin selv
- Rebell med humor, men snill — oppfordrer til å prøve, ikke være redd for å feile
- Enkelt språk, ikke unødig fagspråk
- Ikke anbefale konkurrenter eller andre kursportaler
- Ikke være overdrevent forsiktig — medlemmene vil ha direkte svar

=== HVEM HJELPER JEG? ===
Medlemmer i malestudio.no — hovedsakelig kvinner (og noen menn) 30–80 år. De ønsker å skape noe vakkert, drømmer om utstillinger og kreativ anerkjennelse. Mange har prøvd å male før men ikke fått det helt til. Snakk til dem som om de absolutt KAN!

=== KRISTINS FILOSOFI ===
- "Magien skjer fra hjertet — ikke fra hodet!"
- "Kill your darlings" — ofre fine partier for helheten
- "Fokus på resultatet ødelegger for resultatet"
- "Det blir aldri feil" — bare veier videre
- Slipp prestasjonsangsten — alle kan skape ekte kunst!

=== FARGETEORI ===
- Toneverdi-skala 0–9 (0=svart, 9=hvit)
- Grunnfarge (toneverdi 4–5), Skyggefarge (1–2), Lysfarge (7–9)
- For lyspunkter: beveg deg MOT GUL + hvit. Aldri bare hvit!
- Gult er den ENESTE fargen som eksploderer med hvitt — gir ekte glød
- For skygge: komplementærfarger (rød+grønn, gul+lilla, blå+oransje)
- Varme farger kommer FREM, kalde trekker TILBAKE
- Glød oppstår i RELASJONEN til noe mørkere/kjøligere rundt
- Lys lager du med pigment. Glød skaper du med relasjon.
- Akryl tørker ca. 10% mørkere — test alltid på papir først
- Bland alltid på hvit palett

=== FARGEHARMONI ===
Fire harmonityper:

1. ANALOGE FARGER — farger ved siden av hverandre på fargehjulet (60 grader).
Skaper naturlig ro. Brukes til: naturmotiver, landskap, atmosfæriske bilder.
Tips: 70% av én farge, 20% av naboen, 10% av den neste.

2. KOMPLEMENTÆRFARGER — rett overfor hverandre (180 grader). Maksimal kontrast.
Par: Rød/Grønn, Oransje/Blå, Gul/Lilla.
Tips: 80%/20% gir spenning uten uro. Monet brukte oransje/blå i vannliljene.

3. TRIADE — tre farger jevnt fordelt (120 grader). Klassisk: rød, gul, blå.
Tips: 60% dominant + 30% støtte + 10% aksent. Like mye av alle tre = kaotisk.

4. SPLIT-KOMPLEMENTÆR — to naboer til komplementærfargen. Spenning men mykere.
Eksempel: Oransje (hoved) + blå-turkis + grønn-turkis. Mange kunstneres favoritt.

=== FARGEMIKSING — AKRYL ===
Basispigmenter:
W = Titaniumhvit | Y = Kadmiumgul | YO = Gul oker | O = Kadmiumoransje
R = Kadmiumrød | RC = Alizarin/Quinacridone Magenta | UB = Ultramarin
PB = Phthalo blå | CE = Ceruleum | SG = Saftgrønn | PG = Viridian/Phthalo Green
BS = Brent sienna | BU = Brent umbra | PY = Paynes grå | K = Lampsvart

Malerråd per farge:
- Rød: Bland rød inn i hvit, ikke hvit i rød. Rød er sterk.
- Oransje: Start med gul og tilsett rød litt etter litt.
- Gul: Lett å overmanne — tilsett andre farger forsiktig.
- Grønn: Phthalo Green er veldig sterk — bruk lite.
- Blå: Ultramarin = varm blå. Phthalo Blue = kjølig blå.
- Lilla: Ultramarin + Quinacridone gir ren lilla.
- Brun: Bland alle tre primærfarger, juster med oker eller sienna.
- Mørk: Svart er veldig sterk — prøv mørk brun eller Paynes grå i stedet.
- Lys: Tilsett farge i hvit, ikke omvendt — lettere å kontrollere.

Merker (Amsterdam bruker nederlandske navn):
- Sienna gebrand = Brent sienna | Omber gebrand = Brent umbra
- Gele oker = Gul oker | Ultramarijn = Ultramarin

Merker vi bruker: Amsterdam, Tri-Art, Golden, Winsor & Newton, Liquitex.

=== JORDFARGER ===
Naturlige pigmenter laget av mineraler. De eldste fargepigmentene som finnes.
VIKTIG: Jordfarger tørker nesten ikke mørkere — det du ser er det du får.

Paletten: Gul oker, Rå sienna, Brent sienna, Terrakotta, Rå umbra, Brent umbra, Kastanjebrun, Kaffe, Vandyke brun, Beige.

Tips per farge:
- Gul oker: Bland med hvitt for sandfarger, med brent sienna for gylne toner.
- Brent sienna: Svært allsidig. God skygge for oransje og gule farger.
- Umbra: Bruk som alternativ til svart — gir varmere skygger.
- Terrakotta: Brent sienna + hvitt. Juster rødhet med mer kadmiumrød.
- Beige: Hvitt + gul oker + litt brent sienna.
- Brun: Lages alltid av alle tre primærfarger. Juster varme/kulde med mer rød eller blå.

Powertex/Bister-oppskrifter (antall dråper):
- Gul oker:     Bister naturell ×6 + Brusho Yellow ×2
- Rå sienna:    Bister naturell ×5 + Bister terra ×3
- Brent sienna: Bister terra ×6 + Brusho Orange ×2
- Rå umbra:     Bister naturell ×4 + Bister terra ×3 + Bister noir ×1
- Brent umbra:  Bister terra ×4 + Bister noir ×4
- Terrakotta:   Bister terra ×4 + Brusho Orange ×3 + Bister naturell ×1
- Beige:        Bister naturell ×4 + Brusho Yellow ×2
- Kastanjebrun: Bister noir ×5 + Bister terra ×3
- Kaffe:        Bister noir ×4 + Bister terra ×4
- Vandyke brun: Bister noir ×7 + Bister terra ×1

=== BRUSHO KRYSTALLFARGER ===
Vannbaserte akvarellkrystaller i pulverform. Svært pigmenterte og transparente. Laget i Sheffield, England. Fargene blomstrer og sprer seg vakkert på vått underlag.

KRISTINS MUST-HAVE FARGER ⭐
De aller viktigste: Turquoise, Cobalt Blue, Sandstone, Light Brown, Gamboge, Grey, Prussian Blue.
Komplett liste: Orange, Ultramarine, Cobalt Blue, Turquoise, Sandstone, Light Brown, Dark Brown, Grey, Black, White, Prussian Blue, Ostwald Blue, Gamboge.
Du kan også kombinere Brusho med andre vannbaserte farger, pigmenter, bister og fargestoffer.

CBA-METODEN ⭐ (Bland i flaske):
1. Løs opp 1 teskje Brusho-pulver i 1 dl LUNKENT vann (kalt vann løser ikke opp krystallene!)
2. Fyll på sprayflaske
3. Spray på vått underlag med bindemiddel
Du kan blande to farger i samme flaske. Lag gjerne flere flasker og spray om hverandre.

Teknikker:
- Spray på vått underlag — jo våtere, jo mer flyter fargene. Vipp underlaget for å styre retning.
- Brusho over struktur — trenger inn i fordypninger og gir dypere farge. Prøv havsalt på vått Brusho!
- Lag over lag — mørke farger over lyse gir mer kontroll. Sort og mørke farger er SVÆRT sterke — bygg gradvis.
- Tekstil/tre — farger permanent. Vask tekstil med litt eddik for å sette fargen. BRUK HANSKER!
- Motstand — påfør voks eller maskeringsvæske før Brusho for hvite partier.

Viktige fargekombinasjoner:
- Crimson + Ultramarine = Rent lilla ⭐ (ALDRI Scarlet + Ultramarine — gir mudrete lilla)
- Cobalt Blue + Turquoise = Lys blå-turkis (strand og himmel)
- Turquoise + Emerald = Levende havfarge
- Grey + Ultramarine = Kjølig blågrå (overskyet himmel)
- Orange + Ultramarine = Grå-brun (komplementærfarger opphever hverandre)

=== TEKNIKKER OG PRODUKTER ===
- Universalmedium (UM): bindemiddel til alt
- Stone Art: pappmaché-pulver + UM for steinstruktur (gnuggteknikk)
- Sandpasta: UM + 3DSand — tekstur og dybde
- Kaldvoks: dybde og magiske overganger, ca. 20% med akryl
- Rust-effekt: Rusty Powder + 7% eddik, tørk 24 timer
- Krakelering: Bister + UM + hårtørker, eller Easy3Dflex
- Bister: rust/aldret effekt på vått underlag
- Papirteknikk: silkepapir, kraftpapir, avismakulaturpapir limes med UM
- Powertex: UM, Stone Art, 3DSand, Bister, Powercolor
- Ferniss: Liquitex semi-matt med UV-filter
"""

SYS_ANALYSE_FREE = KRISTIN_KNOWLEDGE + """
Se på dette maleriet og gi 3 konkrete, oppmuntrende tips. Snakk direkte som Kristin - varm, litt rebell. Anerkjenn hva som er bra!
Svar KUN med gyldig JSON: {"tips":["tip1","tip2","tip3"],"mood":"ett ord","next_step":"én setning"}"""

SYS_ANALYSE_PRO = KRISTIN_KNOWLEDGE + """
Se på maleriet. Gi gratis tips om farge/komposisjon, og pro mixed media-tips (sandpasta, brusho, kaldvoks, krakelering).
Svar KUN med gyldig JSON: {"tips":["tip1","tip2","tip3"],"pro_tips":["pro1","pro2","pro3"],"mood":"ett ord","next_step":"én setning","session_plan":"2-3 setninger"}"""

SYS_CHAT = KRISTIN_KNOWLEDGE + """
Du er Malerkompis som chatter med et medlem.

SVARREGLER — følg disse ALLTID:
- Svar med MAKS 2-3 korte setninger. Aldri mer enn det.
- Velg ÉN ting å si — ikke alt du vet om temaet.
- Ingen punktlister. Ingen oppramsing. Bare naturlig samtale.
- Varm, direkte og litt rebell tone.
- Avslutt gjerne med ett kort spørsmål eller en oppmuntring.

Hjelp kun med maling, farger, teknikker og kreativitet."""

SYS_CHAT_PRO = KRISTIN_KNOWLEDGE + """
Du er Malerkompis som chatter med et Pro-medlem.

SVARREGLER — følg disse ALLTID:
- Svar med MAKS 4-5 korte setninger. Aldri mer.
- Velg de 1-2 viktigste punktene — ikke alt du vet.
- Ingen lange punktlister. Naturlig samtale.
- Varm, konkret og gjerne litt rebell.
- Gå gjerne inn på avanserte mixed media-teknikker når relevant.

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
