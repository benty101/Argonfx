from telegram.ext import Updater, CommandHandler

# --- Your Telegram Bot Token ---
TOKEN = "8010024494:AAGsa5y66io5gtPMRupxRY1no2t0aEb3TU0"

def start(update, context):
    update.message.reply_text("Bot is working! 🎉")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
