import json
import os
import json
from datetime import datetime

ACCOUNTS_FILE = "accounts.json"
LOG_FILE = "logs/app.log"


def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"Файл {ACCOUNTS_FILE} не найден")
        return []
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Ошибка чтения JSON: {e}")
            return []

def save_accounts(data):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_event(message):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
