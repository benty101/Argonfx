import os
import time
from notion_client import Client
from telegram import Bot

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_GROUP_ID")  # should be like -1002853745494

notion = Client(auth=NOTION_TOKEN)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_new_trades():
    # Find all trades where "Post to Telegram" = True (checkbox property)
    result = notion.databases.query(
        **{
            "database_id": NOTION_DB_ID,
            "filter": {
                "property": "Post to Telegram",
                "checkbox": {"equals": True}
            }
        }
    )
    return result["results"]

def format_trade(page):
    props = page["properties"]
    pair = props.get("Pair", {}).get("title", [{}])[0].get("plain_text", "N/A")
    bias = props.get("Bias", {}).get("select", {}).get("name", "")
    entry = props.get("Entry", {}).get("rich_text", [{}])[0].get("plain_text", "")
    sl = props.get("SL", {}).get("rich_text", [{}])[0].get("plain_text", "")
    tp1 = props.get("TP1", {}).get("rich_text", [{}])[0].get("plain_text", "")
    msg = f"📊 {pair}\nBias: {bias}\nEntry: {entry}\nSL: {sl}\nTP1: {tp1}"
    return msg

def main():
    sent = set()
    while True:
        try:
            pages = fetch_new_trades()
            for page in pages:
                page_id = page["id"]
                if page_id in sent:
                    continue
                msg = format_trade(page)
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
                sent.add(page_id)
        except Exception as e:
            print("Error:", e)
        time.sleep(60)  # check every 1 minute

if __name__ == "__main__":
    main()
