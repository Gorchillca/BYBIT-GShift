
import json
import os
from crypto_utils import encrypt_string, decrypt_string
from datetime import datetime

ACCOUNTS_FILE = "accounts.json"
LOG_FILE = "logs/app.log"

def log_event(message):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def save_accounts(accounts):
    encrypted_accounts = []
    for acc in accounts:
        encrypted_accounts.append({
            "label": acc["label"],
            "api_key": encrypt_string(acc["api_key"]),
            "api_secret": encrypt_string(acc["api_secret"])
        })
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(encrypted_accounts, f, indent=2)

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        decrypted = []
        for acc in data:
            decrypted.append({
                "label": acc["label"],
                "api_key": decrypt_string(acc["api_key"]),
                "api_secret": decrypt_string(acc["api_secret"])
            })
        return decrypted
    except Exception as e:
        log_event(f"[ERR] Не удалось загрузить аккаунты: {e}")
        return []
