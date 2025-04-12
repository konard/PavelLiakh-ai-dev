import json
from src.config import config

SESSION_FILE = config.get_folder("sessions") / 'sessions.json'

def load_sessions() -> dict:
    return json.loads(SESSION_FILE.read_text()) if SESSION_FILE.exists() else {}

def save_sessions(sessions: dict):
    SESSION_FILE.write_text(json.dumps(sessions))