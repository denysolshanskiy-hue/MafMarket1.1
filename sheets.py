import gspread
import os
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_client():
    # Отримуємо приватний ключ і виправляємо символи переносу рядка
    private_key = os.getenv("G_PRIVATE_KEY")
    if private_key:
        private_key = private_key.replace('\\n', '\n')

    # Створюємо словник конфігурації прямо в коді
    creds_dict = {
        "type": "service_account",
        "project_id": os.getenv("G_PROJECT_ID"),
        "private_key_id": os.getenv("G_PRIVATE_KEY_ID"),
        "private_key": private_key,
        "client_email": os.getenv("G_CLIENT_EMAIL"),
        "client_id": os.getenv("G_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.google.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("G_CERT_URL")
    }
    
    # Перевірка чи всі важливі дані на місці
    if not creds_dict["private_key"] or not creds_dict["client_email"]:
        raise ValueError("Критичні дані Google (Email або Key) відсутні в налаштуваннях Koyeb!")

    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def get_spreadsheet():
    return get_client().open(os.getenv("SPREADSHEET_NAME"))

def get_players_sheet():
    return get_spreadsheet().worksheet("Гравці🕵️‍♂️")

def find_player_by_nick(nick: str):
    ws = get_players_sheet()
    rows = ws.get_all_values()
    for i, row in enumerate(rows[1:], 2):
        if len(row) > 1 and row[1].strip().lower() == nick.strip().lower():
            return i, row
    return None, None

def bind_telegram_id(row_index: int, telegram_id: int):
    # Тут була головна проблема: права доступу або невірний індекс
    get_players_sheet().update_cell(row_index, 4, str(telegram_id))

def get_balance_by_telegram_id(telegram_id: int):
    players = get_players_sheet().get_all_values()
    nick = next((r[1] for r in players[1:] if len(r) > 3 and str(r[3]) == str(telegram_id)), None)
    if not nick: return None

    rows = get_spreadsheet().worksheet("Авто-баланс🤑").get_all_values()
    for r in rows[1:]:
        if r[0].strip().lower() == nick.strip().lower():
            # Захист від пустих клітинок та ком замість точок
            def to_int(val):
                try: return int(float(str(val).replace(',', '.')))
                except: return 0
            return {"nick": r[0], "total": to_int(r[3]), "spent": to_int(r[2])}
    return None

def get_market_items():
    rows = get_spreadsheet().worksheet("🖤MafMarket🖤").get_all_values()
    return [{"name": r[0], "price": r[1], "description": r[2], "level": r[3]} for r in rows[2:] if r[0]]

def add_purchase(nick: str, item_name: str, price: int):
    get_spreadsheet().worksheet("Покупки🛒").append_row([datetime.now().strftime("%d.%m.%Y"), nick, item_name, price])

def get_progress_by_nick(nick: str):
    rows = get_spreadsheet().worksheet("Прогрес📊").get_all_values()
    for r in rows[1:]:
        if r[0].strip().lower() == nick.strip().lower():
            return {"nick": r[0], "balance": r[1], "available": r[2], "status": r[3]}
    return None

def get_next_goal(balance: int):
    for item in get_market_items():
        try:
            price = int(item["price"])
            if balance < price:
                return {"name": item["name"], "price": price, "remaining": price - balance}
        except: continue
    return None
def get_market_item_by_name(name: str):
    items = get_market_items()
    search = name.strip().lower()
    return next((i for i in items if i['name'].strip().lower() == search), None)


