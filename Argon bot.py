# argon_bot.py

from telegram import Bot
from notion_client import Client
import time
import os

# === CONFIGURATION FROM ENV VARIABLES ===
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === INITIALIZE CLIENTS ===
notion = Client(auth=NOTION_TOKEN)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# === FORMAT TELEGRAM MESSAGE ===
def format_trade_message(properties):
    return f"""
📉 ARGON FX SIGNAL – {properties['Date']['date']['start']}

Pair: {properties['Pair']['title'][0]['plain_text']}
Bias: {properties['Bias']['select']['name']}
Entry: {properties['Entry']['number']}
SL: {properties['SL']['number']}
TP1: {properties['TP1']['number']}
TP2: {properties['TP2']['number']}
Model: {properties['Model']['rich_text'][0]['plain_text']} | Session: {properties['Session']['select']['name']}

Status: {properties['Status']['select']['name']}
Notes: {properties['Notes']['rich_text'][0]['plain_text'] if properties['Notes']['rich_text'] else ''}
"""

# === MAIN BOT FUNCTION ===
def check_and_post():
    response = notion.databases.query(database_id=DATABASE_ID)
    for page in response['results']:
        props = page['properties']
        if props['Post to Telegram']['checkbox']:
            message = format_trade_message(props)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

            # Uncheck the box after posting
            notion.pages.update(
                page_id=page['id'],
                properties={
                    "Post to Telegram": {"checkbox": False}
                }
            )

# === LOOP (runs every 10 min) ===
if __name__ == "__main__":
    while True:
        try:
            check_and_post()
            time.sleep(600)
        except Exception as e:
            print("Error:", e)
            time.sleep(60)
