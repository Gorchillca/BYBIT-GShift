# BYBIT GShift

Утилита для безопасного перевода средств между аккаунтами Bybit через API. Есть N-ное количество кошельков и один финальный. Парсит балансы с N-ного количества кошельков, переводит все на один финальный кошелек. Работает локально, поддерживает:


- управление аккаунтами (API-ключи)
- отправку USDT TRC20 на финальный UID/email
- автообновление баланса
- адресную книгу получателей
- графический интерфейс в стиле GNOME

## Скриншоты

(давай потом братка)

## Установка

1. Склонируй репозиторий
2. Установи зависимости:  
   `pip install -r requirements.txt`
3. Запусти:  
   `python gui.py`

## Безопасность

Программа работает **локально**, ключи не передаются в интернет.  
Будет добавлено: шифрование и автообновления.
