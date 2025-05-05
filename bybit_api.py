import time
import hmac
import hashlib
import requests
import json
from utils import load_accounts, log_event

BASE_URL = "https://api.bybit.com"


def generate_signature(api_key, api_secret, timestamp, recv_window, body):
    param_str = f'{timestamp}{api_key}{recv_window}{body}'
    return hmac.new(
        bytes(api_secret, 'utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def get_balance(api_key, api_secret):
    import time, hmac, hashlib, requests

    url = "https://api.bybit.com/v5/account/wallet-balance"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    query_string = "accountType=UNIFIED"

    signature_payload = f"{timestamp}{api_key}{recv_window}{query_string}"
    signature = hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(signature_payload, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window
    }

    params = {"accountType": "UNIFIED"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # <-- теперь кидает ошибку если 401 или 404

    data = response.json()
    if data["retCode"] != 0:
        raise Exception(f"API error: {data['retMsg']}")

    for coin in data["result"]["list"][0]["coin"]:
        if coin["coin"] == "USDT":
            return float(coin["walletBalance"])

    return 0.0

def withdraw_to_uid(api_key, api_secret, uid, amount):
    endpoint = "/v5/asset/withdraw/create"
    url = BASE_URL + endpoint
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    body_dict = {
        "coin": "USDT",
        "address": uid,  # UID получателя вместо адреса
        "amount": str(amount),
        "forceChain": 2,  # внутренний перевод по UID
        "accountType": "FUND"
    }
    body = json.dumps(body_dict)
    sign = generate_signature(api_key, api_secret, timestamp, recv_window, body)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": sign,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()
        resp_json = response.json()
        if resp_json.get("retCode") == 0:
            log_event(f"[OK] Отправлено {amount} USDT на UID {uid}")
            return True
        else:
            log_event(f"[ERR] Ошибка перевода: {resp_json}")
    except Exception as e:
        log_event(f"[ERR] Ошибка запроса на перевод: {e}")
    return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("❌ Укажи финальный UID как аргумент: python main.py 12345678")
        exit(1)

    final_uid = sys.argv[1].strip()
    accounts = load_accounts()
    for acc in accounts:
        api_key = acc["api_key"]
        api_secret = acc["api_secret"]
        label = acc.get("label", "Безымянный")
        balance = get_balance(api_key, api_secret)
        print(f"{label}: {balance} USDT")
        if balance >= 10:
            withdraw_to_uid(api_key, api_secret, final_uid, balance)
        else:
            log_event(f"[SKIP] {label} — баланс меньше 10 USDT")
