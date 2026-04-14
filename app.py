import os, json, re, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_DIR = Path(__file__).parent
HTML = (BASE_DIR / "index.html").read_text()

SYS_FREE = 'Du er en erfaren akrylmaling og mixed media-lærer. Se på elevens maleri og gi 3 konkrete, oppmuntrende tips. Fokuser på komposisjon, fargebruk og én teknikk. Svar KUN med gyldig JSON, ingen annen tekst, ingen backticks: {"tips":["tip1","tip2","tip3"],"mood":"ett ord","next_step":"én setning"}'
SYS_PRO  = 'Du er en erfaren akrylmaling og mixed media-lærer. Gi råd på to nivåer. Svar KUN med gyldig JSON, ingen annen tekst, ingen backticks: {"tips":["tip1","tip2","tip3"],"pro_tips":["protip1","protip2","protip3"],"mood":"ett ord","next_step":"én setning","session_plan":"2-3 setninger"}'

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path != "/analyze":
            self.send_error(404); return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        api_key = API_KEY or body.get("api_key", "").strip()
        image = body.get("image", "")
        level = body.get("level", "free")

        if not api_key:
            self._json({"error": "Ingen API-nøkkel konfigurert."}, 400); return

        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": SYS_FREE if level == "free" else SYS_PRO,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image}},
                {"type": "text", "text": "Her er maleriet mitt. Gi meg tips."}
            ]}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
        )
        try:
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
            raw = "".join(i.get("text","") for i in data.get("content",[])).strip()
            m = re.search(r'\{[\s\S]*\}', raw)
            if not m: self._json({"error": "Prøv igjen."}, 500); return
            self._json(json.loads(m.group()))
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
