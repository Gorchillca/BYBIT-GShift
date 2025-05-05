import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from bybit_api import get_balance, withdraw_to_uid
from utils import load_accounts, save_accounts, log_event
import json
import os

ADDRESS_BOOK_FILE = "address_book.json"
LOGO_PATH = "logo_g.png"


def load_address_book():
    try:
        with open(ADDRESS_BOOK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_address_book(book):
    with open(ADDRESS_BOOK_FILE, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=2, ensure_ascii=False)


def confirm_and_transfer():
    selected = address_combobox.get()
    if not selected:
        messagebox.showwarning("Ошибка", "Выбери получателя")
        return

    try:
        min_amount = float(min_amount_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Минимальный порог должен быть числом")
        return

    recipient = next((a for a in address_book if a["label"] == selected), None)
    if not recipient:
        messagebox.showerror("Ошибка", "Получатель не найден")
        return

    if not messagebox.askyesno("Подтверждение",
        f"Перевести все доступные USDT на: {recipient['value']}?\nПорог: {min_amount} USDT"):
        return

    uid = recipient["value"]
    balances_text.delete("1.0", tk.END)
    for acc in accounts:
        label = acc["label"]
        key = acc["api_key"]
        secret = acc["api_secret"]
        balance = get_balance(key, secret)
        balances_text.insert(tk.END, f"{label}: {balance} USDT\n")
        if balance >= min_amount:
            success = withdraw_to_uid(key, secret, uid, balance)
            if success:
                balances_text.insert(tk.END, f"→ Отправлено {balance} USDT на {uid}\n")
        else:
            balances_text.insert(tk.END, f"[Пропущено] Баланс < {min_amount} USDT\n")
        balances_text.insert(tk.END, "\n")
        balances_text.see(tk.END)


def add_recipient():
    win = tb.Toplevel(root)
    win.title("Новый получатель")
    win.geometry("420x240")

    tb.Label(win, text="Название (label):").pack(pady=(10, 2))
    label_entry = tb.Entry(win, width=30)
    label_entry.pack(pady=2)

    tb.Label(win, text="UID или email:").pack(pady=(10, 2))
    val_entry = tb.Entry(win, width=30)
    val_entry.pack(pady=2)

    def save():
        label = label_entry.get().strip()
        value = val_entry.get().strip()
        if not label or not value:
            messagebox.showwarning("Ошибка", "Все поля обязательны")
            return
        address_book.append({"label": label, "value": value})
        save_address_book(address_book)
        address_combobox["values"] = [a["label"] for a in address_book]
        address_combobox.set(label)
        win.destroy()

    tb.Button(win, text="💾 Сохранить", command=save, bootstyle=INFO).pack(pady=12)


def add_account():
    win = tb.Toplevel(root)
    win.title("Новый аккаунт")
    win.geometry("420x300")

    tb.Label(win, text="Название (label):").pack(pady=(10, 2))
    label_entry = tb.Entry(win, width=30)
    label_entry.pack()

    tb.Label(win, text="API Key:").pack(pady=(10, 2))
    key_entry = tb.Entry(win, width=30)
    key_entry.pack()

    tb.Label(win, text="API Secret:").pack(pady=(10, 2))
    secret_entry = tb.Entry(win, width=30, show="*")
    secret_entry.pack()

    def save():
        label = label_entry.get().strip()
        key = key_entry.get().strip()
        secret = secret_entry.get().strip()
        if not label or not key or not secret:
            messagebox.showwarning("Ошибка", "Все поля обязательны")
            return
        accounts.append({"label": label, "api_key": key, "api_secret": secret})
        save_accounts(accounts)
        refresh_account_list()
        win.destroy()

    tb.Button(win, text="💾 Сохранить аккаунт", command=save, bootstyle=INFO).pack(pady=15)


def refresh_account_list():
    account_listbox.delete(0, tk.END)
    for acc in accounts:
        short_key = acc["api_key"][-4:]
        balance = get_balance(acc["api_key"], acc["api_secret"])
        account_listbox.insert(tk.END, f"{acc['label']} (••••{short_key})  —  {balance} USDT")


def delete_selected_account():
    idx = account_listbox.curselection()
    if not idx:
        messagebox.showwarning("Ошибка", "Выбери аккаунт для удаления")
        return
    if not messagebox.askyesno("Подтверждение", "Удалить выбранный аккаунт?"):
        return
    del accounts[idx[0]]
    save_accounts(accounts)
    refresh_account_list()


def delete_selected_recipient():
    selected = address_combobox.get()
    if not selected:
        messagebox.showwarning("Ошибка", "Выбери получателя для удаления")
        return
    if not messagebox.askyesno("Подтверждение", "Удалить выбранного получателя?"):
        return
    global address_book
    address_book = [a for a in address_book if a["label"] != selected]
    save_address_book(address_book)
    address_combobox["values"] = [a["label"] for a in address_book]
    address_combobox.set("")


root = tb.Window(themename="darkly")
root.title("BYBIT GShift")
root.geometry("760x720")

accounts = load_accounts()
address_book = load_address_book()

frame_main = tb.Frame(root, padding=20)
frame_main.pack(fill=BOTH, expand=True)

header_frame = tb.Frame(frame_main)
header_frame.pack(pady=(0, 25))
inner_header = tb.Frame(header_frame)
inner_header.pack(anchor='center')

if os.path.exists(LOGO_PATH):
    logo = tk.PhotoImage(file=LOGO_PATH).subsample(6, 6)
    logo_label = tk.Label(inner_header, image=logo, bg="#2e2e2e")
    logo_label.image = logo
    logo_label.pack(side=LEFT, padx=(0, 10))

header = tb.Label(inner_header, text="BYBIT GShift", font=("Segoe UI", 18, "bold"), foreground="#d4d4d4")
header.pack(side=LEFT)

# --- Аккаунты ---
tb.Label(frame_main, text="Ваши аккаунты:", foreground="#d4d4d4").pack(anchor="w")
account_listbox = tk.Listbox(frame_main, height=5, bg="#1e1e1e", fg="#d4d4d4", font=("Courier", 10))
account_listbox.pack(fill=X, pady=5)

acc_btns = tb.Frame(frame_main)
acc_btns.pack(pady=(0, 10))

btn_add_account = tb.Button(acc_btns, text="➕ Добавить аккаунт", command=add_account, bootstyle=SECONDARY)
btn_add_account.pack(side=LEFT, padx=5)

btn_refresh_bal = tb.Button(acc_btns, text="🔄 Обновить балансы", command=refresh_account_list, bootstyle=INFO)
btn_refresh_bal.pack(side=LEFT, padx=5)

btn_delete_account = tb.Button(acc_btns, text="🗑 Удалить аккаунт", command=delete_selected_account, bootstyle=DANGER)
btn_delete_account.pack(side=LEFT, padx=5)

# --- Перевод ---
row1 = tb.Frame(frame_main)
row1.pack(fill=X, pady=10)

tb.Label(row1, text="Куда перевести:", foreground="#d4d4d4").pack(side=LEFT)
address_combobox = tb.Combobox(row1, values=[a["label"] for a in address_book], width=40)
address_combobox.pack(side=LEFT, padx=10)

btn_add_recipient = tb.Button(row1, text="➕ Новый получатель", command=add_recipient, bootstyle=SECONDARY)
btn_add_recipient.pack(side=LEFT)

btn_del_recipient = tb.Button(row1, text="🗑", command=delete_selected_recipient, bootstyle=DANGER)
btn_del_recipient.pack(side=LEFT, padx=5)

row2 = tb.Frame(frame_main)
row2.pack(fill=X, pady=10)

tb.Label(row2, text="Мин. сумма для перевода (USDT):", foreground="#d4d4d4").pack(side=LEFT)
min_amount_entry = tb.Entry(row2, width=10)
min_amount_entry.insert(0, "1.0")
min_amount_entry.pack(side=LEFT, padx=10)

btn_transfer = tb.Button(row2, text="🚀 Перевести средства", command=confirm_and_transfer, bootstyle=INFO)
btn_transfer.pack(side=LEFT, padx=15)

# --- Лог ---
tb.Label(frame_main, text="Лог операций:", foreground="#d4d4d4").pack(anchor="w", pady=(20, 5))
balances_text = tk.Text(frame_main, height=16, bg="#1e1e1e", fg="#d4d4d4", font=("JetBrains Mono", 10), wrap=WORD, bd=0, highlightthickness=0)
balances_text.pack(fill=BOTH, expand=True)

refresh_account_list()
root.mainloop()
