import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
executable = ROOT / ".venv" / "bin" / "phoenix"
if not executable.exists():
    raise SystemExit("Install requirements-phoenix.txt in a Python 3.13 .venv first.")

environment = os.environ.copy()
environment["PHOENIX_HOST"] = "127.0.0.1"
environment["PHOENIX_PORT"] = "6006"
environment["PHOENIX_WORKING_DIR"] = str(ROOT / "results" / "private" / "phoenix")
os.execve(str(executable), [str(executable), "serve"], environment)
