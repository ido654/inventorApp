from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes ,MessageHandler ,filters ,  ConversationHandler
from handlers.handlers import start_command , daily_count_command  , records_command
from conversations.add_record import ask_item_id  ,ASK_ITEM_ID ,cancel ,  new_record_command
from conversations.return_item import return_command , ask_items , ASK_ITEM_ID ,cancel 
from conversations.history_record import get_history_command , ASK_DAYES , ask_days, cancel
from conversations.registration import ASK_DISPLAY_NAME , start_registration , cancel , handle_registration_name
from dotenv import load_dotenv
import os
load_dotenv()

TOKEN= os.environ.get('TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME')


if __name__ == "__main__":
    print("Starting bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    # פקודות
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("daily_count", daily_count_command))
    app.add_handler(CommandHandler("show", records_command))
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
    print("Bot is running...")
    app.run_polling(poll_interval=3)


