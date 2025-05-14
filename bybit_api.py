import time
import hmac
import hashlib
import requests
import json
from utils import load_accounts, log_event
from decimal import Decimal, ROUND_DOWN
from uuid import uuid4

BASE_URL = "https://api.bybit.com"


def generate_signature(api_key, api_secret, timestamp, recv_window, body):
    msg = f"{timestamp}{api_key}{recv_window}{body}"
    return hmac.new(
        api_secret.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def get_balance(api_key, api_secret):
    url = f"{BASE_URL}/v5/account/wallet-balance"
    timestamp = str(int(time.time() * 1000))
    recv_window = "30000"
    query = "accountType=UNIFIED"

    sign = generate_signature(api_key, api_secret, timestamp, recv_window, query)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": sign,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window
    }
    params = {"accountType": "UNIFIED"}

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    if data.get("retCode") != 0:
        raise Exception(f"API error: {data.get('retMsg')}")

    for entry in data.get("result", {}).get("list", []):
        for coin in entry.get("coin", []):
            if coin.get("coin") == "USDT":
                return float(coin.get("walletBalance", 0))
    return 0.0


def transfer_to_uid(api_key, api_secret, to_uid, amount):
    url = f"{BASE_URL}/v5/asset/internal-transfer"
    timestamp = str(int(time.time() * 1000))
    recv_window = "30000"

    amount = Decimal(str(amount)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
    if amount <= 0:
        log_event(f"[SKIP] Пропущен перевод с нулевой суммой: {amount}")
        return False

    transfer_id = str(uuid4())
    body_dict = {
        "transferId": transfer_id,
        "transferMethod": "UID",
        "coin": "USDT",
        "amount": str(amount),
        "fromAccountType": "UNIFIED",
        "toAccountType": "UNIFIED",
        "toMemberId": to_uid
    }

    body = json.dumps(body_dict, separators=(',', ':'), ensure_ascii=False)
    sign = generate_signature(api_key, api_secret, timestamp, recv_window, body)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": sign,
        "X-BAPI-SIGN-TYPE": "2",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, headers=headers, data=body)
        resp.raise_for_status()
        result = resp.json()
        if result.get("retCode") == 0:
            log_event(f"[OK] Переведено {amount} USDT на UID {to_uid}")
            return True
        else:
            log_event(f"[ERR] Ошибка перевода: {result}")
    except Exception as e:
        log_event(f"[ERR] Ошибка запроса transfer: {e}")
    return False



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python bybit_api.py <API_KEY> <API_SECRET> <UID>")
        exit(1)

    api_key, api_secret, uid = sys.argv[1], sys.argv[2], sys.argv[3]
    bal = get_balance(api_key, api_secret)
    print(f"Текущий баланс: {bal} USDT")
    transfer_to_uid(api_key, api_secret, uid, bal)
