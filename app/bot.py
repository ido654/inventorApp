from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes ,MessageHandler ,filters ,  ConversationHandler
from handlers.handlers import start_command , daily_count_command  , records_command
from conversations.add_record import ask_item_id  ,ASK_ITEM_ID ,cancel ,  new_record_command
from conversations.return_item import return_command , ask_items , ASK_ITEM_ID ,cancel 
from conversations.history_record import get_history_command , ASK_DAYES , ask_days, cancel
from conversations.registration import ASK_DISPLAY_NAME , start_registration , cancel , handle_registration_name
from dotenv import load_dotenv
from db.db import init_db
import os

load_dotenv()

BOT_TOKEN= os.environ.get('TELEGRAM_BOT_TOKEN' , 'TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get('PORT', 8080))
BOT_USERNAME = os.environ.get('BOT_USERNAME')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN must be set as an environment variable.")


if __name__ == "__main__":
    print("Starting bot...")


    app = ApplicationBuilder().token(BOT_TOKEN).build()
    init_db()
    # פקודות
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("daily_count", daily_count_command))
    app.add_handler(CommandHandler("records", records_command))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("register" , start_registration)],
        states={
            ASK_DISPLAY_NAME : [MessageHandler(filters.TEXT & ~filters.COMMAND , handle_registration_name )]
        },
        fallbacks=[CommandHandler("cancel" , cancel)]
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("new_record" ,new_record_command)],
        states={
            ASK_ITEM_ID : [MessageHandler(filters.TEXT & ~filters.COMMAND , ask_item_id )]
        },
        fallbacks=[CommandHandler("cancel" , cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("return" ,return_command )],
        states={
            ASK_ITEM_ID : [MessageHandler(filters.TEXT & ~filters.COMMAND ,ask_items)]
        },
        fallbacks=[CommandHandler("cancel" , cancel)]
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("history" ,get_history_command )],
        states={
            ASK_DAYES : [MessageHandler(filters.TEXT & ~filters.COMMAND ,ask_days)]
        },
        fallbacks=[CommandHandler("cancel" , cancel)]
    ))

    if WEBHOOK_URL:
        print(f"Starting in Webhook mode. Listening on port {PORT}.")
        # הפעלת שרת HTTP קטן המאזין לבקשות מטלגרם
        app.run_webhook(
            listen="0.0.0.0", # האזנה לכל הממשקים
            port=PORT,
            url_path=BOT_TOKEN,  # שימוש בטוקן כנתיב סודי
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
        )
    else:
        print("Starting in Polling mode (WEBHOOK_URL not set).")
        app.run_polling(poll_interval=3)


