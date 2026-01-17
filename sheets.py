import gspread
import base64
import json
import os
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client():
    b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
    if not b64:
        raise RuntimeError("GOOGLE_CREDENTIALS_B64 is missing")

    creds_json = base64.b64decode(b64).decode("utf-8")
    creds_dict = json.loads(creds_json)

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )
    return gspread.authorize(creds)


def get_spreadsheet():
    name = os.getenv("SPREADSHEET_NAME")
    if not name:
        raise RuntimeError("SPREADSHEET_NAME is missing")

    return get_client().open(name)


def get_players_sheet():
    return get_spreadsheet().worksheet("Гравці🕵️‍♂️")

def find_player_by_nick(nick: str):
    ws = get_players_sheet()
    rows = ws.get_all_values()  # всі рядки як список списків

    # rows[0] — заголовки
    for i in range(1, len(rows)):
        sheet_nick = rows[i][1].strip()  # колонка B = Нік
        if sheet_nick == nick:
            return i + 1, rows[i]  # +1 бо Google Sheets з 1
    return None, None

def bind_telegram_id(row_index: int, telegram_id: int):
    ws = get_players_sheet()
    ws.update_cell(row_index, 4, telegram_id)  # колонка D

def get_balance_by_telegram_id(telegram_id: int):
    players_ws = get_players_sheet()
    players = players_ws.get_all_values()

    nick = None
    for i in range(1, len(players)):
        if str(players[i][3]) == str(telegram_id):  # колонка D = telegram_id
            nick = players[i][1]  # колонка B = Нік
            break

    if not nick:
        return None

    balance_ws = get_spreadsheet().worksheet("Авто-баланс🤑")
    rows = balance_ws.get_all_values()

    for i in range(1, len(rows)):
        if rows[i][0] == nick:  # колонка A = Нік
            total = rows[i][1] or "0"
            spent = rows[i][2] or "0"
            return {
    "nick": rows[i][0],
    "total": int(rows[i][3]),     # ПОТОЧНИЙ БАЛАНС
    "spent": int(rows[i][2]),
}


    return None

def get_market_items():
    ws = get_spreadsheet().worksheet("🖤MafMarket🖤")
    rows = ws.get_all_values()

    items = []

    for i in range(2, len(rows)):  # пропускаємо 1-й і 2-й рядки
        if not rows[i][0]:
            continue

        items.append({
            "name": rows[i][0],
            "price": rows[i][1],
            "description": rows[i][2],
            "level": rows[i][3],
        })

    return items

from datetime import datetime

def add_purchase(nick: str, item_name: str, price: int):
    ws = get_spreadsheet().worksheet("Покупки🛒")

    ws.append_row([
        datetime.now().strftime("%d.%m.%Y"),
        nick,
        item_name,
        price,
    ])
def normalize(text: str) -> str:
    return text.strip().lower()

def get_market_item_by_name(name: str):
    search = normalize(name)
    items = get_market_items()

    for item in items:
        if normalize(item["name"]) == search:
            return item

    return None

def get_progress_by_nick(nick: str):
    ws = get_spreadsheet().worksheet("Прогрес")
    rows = ws.get_all_values()

    for i in range(1, len(rows)):
        if rows[i][0].strip().lower() == nick.strip().lower():
            return {
                "nick": rows[i][0],
                "balance": rows[i][1],
                "available": rows[i][2],
                "status": rows[i][3],
            }

    return None
def get_progress_by_nick(nick: str):
    ws = get_spreadsheet().worksheet("Прогрес📊")
    rows = ws.get_all_values()

    for i in range(1, len(rows)):
        if rows[i][0].strip().lower() == nick.strip().lower():
            return {
                "nick": rows[i][0],
                "balance": rows[i][1],
                "available": rows[i][2],
                "status": rows[i][3],
            }

    return None

def get_next_goal(balance: int):
    items = get_market_items()

    for item in items:
        price = int(item["price"])
        if balance < price:
            return {
                "name": item["name"],
                "price": price,
                "remaining": price - balance,
            }

    return None
