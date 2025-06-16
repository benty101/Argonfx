import os
import time
from notion_client import Client
from telegram import Bot

# Load environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_GROUP_ID")  # e.g., -1002853745494

# Check that all required environment variables are set
required_env = {
    "NOTION_TOKEN": NOTION_TOKEN,
    "NOTION_DATABASE_ID": NOTION_DATABASE_ID,
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_GROUP_ID": TELEGRAM_CHAT_ID
}
for key, value in required_env.items():
    if value is None:
        print(f"Error: Environment variable {key} is not set!")
        exit(1)

notion = Client(auth=NOTION_TOKEN)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_new_trades():
    try:
        result = notion.databases.query(
            **{
                "database_id": NOTION_DATABASE_ID,
                "filter": {
                    "property": "Post to Telegram",
                    "checkbox": {"equals": True}
                }
            }
        )
        return result.get("results", [])
    except Exception as e:
        print("Error querying Notion:", e)
        import traceback
        traceback.print_exc()
        return []

def format_trade(page):
    props = page.get("properties", {})

    def safe_get(prop, typ):
        try:
            items = props.get(prop, {}).get(typ, [])
            return items[0].get("plain_text", "")
        except Exception:
            return ""
    
    # Pair (title property)
    pair = safe_get("Pair", "title") or "N/A"

    # Bias (select property)
    bias = ""
    try:
        bias_select = props.get("Bias", {}).get("select")
        if bias_select:
            bias = bias_select.get("name", "")
    except Exception:
        bias = ""

    entry = safe_get("Entry", "rich_text")
    sl = safe_get("SL", "rich_text")
    tp1 = safe_get("TP1", "rich_text")

    msg = f"📊 {pair}\nBias: {bias}\nEntry: {entry}\nSL: {sl}\nTP1: {tp1}"
    return msg

def main():
    sent = set()
    while True:
        try:
            pages = fetch_new_trades()
            print(f"DEBUG: {len(pages)} pages fetched from Notion.")
            for page in pages:
                page_id = page.get("id")
                if not page_id or page_id in sent:
                    continue
                msg = format_trade(page)
                print(f"Sending to Telegram: {msg}")
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
                sent.add(page_id)
        except Exception as e:
            print("Error:", e)
            import traceback
            traceback.print_exc()
        time.sleep(60)  # check every 1 minute

if __name__ == "__main__":
    main()
