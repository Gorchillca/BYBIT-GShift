
from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

fernet = Fernet(load_key())

def encrypt_string(plain_text: str) -> str:
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_string(encrypted_text: str) -> str:
    return fernet.decrypt(encrypted_text.encode()).decode()
