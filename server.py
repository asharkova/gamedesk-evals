import argparse
import getpass
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from gamedesk_model import ChatError, DEFAULT_MODEL, MODELS, ROOT, generate_answer, load_configuration
from gamedesk_tracing import flush_traces, initialize_tracing


def make_handler(configuration, requirements):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT / "ui" / "dist"), **kwargs)

        def log_message(self, format_string, *args):
            pass

        def send_json(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def valid_host(self):
            return self.headers.get("Host") in {
                f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}",
            }

        def do_GET(self):
            if not self.valid_host():
                self.send_json(403, {"error": "Localhost access only."})
            elif self.path == "/api/status":
                self.send_json(200, {
                    "configured": bool(configuration["key"]) and configuration["model"] in MODELS,
                    "model": configuration["model"], "provider": "Groq",
                    "connection_verified": False,
                })
            else:
                super().do_GET()

        def do_POST(self):
            if self.path != "/api/chat":
                self.send_json(404, {"error": "Unknown endpoint."})
                return
            allowed_origins = {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}
            if not self.valid_host() or self.headers.get("Origin") not in allowed_origins | {None}:
                self.send_json(403, {"error": "Use the local GameDesk interface."})
                return
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                self.send_json(415, {"error": "Send JSON content."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 16384:
                    raise ChatError("The request is empty or too large.", 413)
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ChatError("Send a question as a JSON object.", 400)
                question = body.get("question")
                context = body.get("scenario_context", "")
                if not isinstance(question, str) or not 0 < len(question.strip()) <= 2000:
                    raise ChatError("Enter a question between 1 and 2,000 characters.", 400)
                if not isinstance(context, str) or len(context) > 1000:
                    raise ChatError("The scenario context is invalid.", 400)
                result = generate_answer(question.strip(), context, configuration, requirements)
                self.send_json(200, result)
            except (ValueError, UnicodeDecodeError):
                self.send_json(400, {"error": "Invalid JSON request."})
            except ChatError as error:
                self.send_json(error.status, {"error": str(error)})

    return Handler


def main():
    parser = argparse.ArgumentParser(description="Run GameDesk locally with a hosted Groq model.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--setup-key", action="store_true")
    args = parser.parse_args()
    if args.setup_key:
        key = getpass.getpass("Paste your Groq Free-plan key (input hidden): ").strip()
        if not key or any(character.isspace() for character in key):
            parser.error("The key must be non-empty and contain no whitespace.")
        path = ROOT / ".env"
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w") as handle:
            handle.write(f"GROQ_API_KEY={key}\nGROQ_MODEL={DEFAULT_MODEL}\n")
        print("Key saved locally in ignored .env. Run: python3 server.py")
        return
    configuration = load_configuration()
    if initialize_tracing():
        print("Phoenix tracing enabled: project gamedesk at http://127.0.0.1:6006")
    requirements = json.loads((ROOT / "requirements.json").read_text())
    for filename in ("requirements.json", "cases.json"):
        (ROOT / "ui" / "dist" / filename).write_bytes((ROOT / filename).read_bytes())
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(configuration, requirements))
    print(f"GameDesk: http://127.0.0.1:{server.server_port}")
    print("Groq key configured; not yet verified." if configuration["key"] else "Reference mode available. Set up a key to enable live AI.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        flush_traces()


if __name__ == "__main__":
    main()
