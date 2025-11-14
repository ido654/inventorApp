from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db.db import get_inventory_summary ,get_active_records , get_user_display_name
from db.test_db import make_table
from prettytable import PrettyTable

async def start_command (update: Update , context : ContextTypes.DEFAULT_TYPE ):
    user = update.effective_user
    user_id = user.id
    user_name = get_user_display_name(user_id)
    commands = [
        "/new_record - לקיחת פריט חדש",
        "/return - החזרת פריט",
        "/records - הצגת פריטים פעילים",
        "/history - היסטוריית לקיחות/החזרות",
        "/daily_count - סיכום מלאי לפי קטגוריה",
        "/register -  החלפת שם" ,
    ]
    commands_text = "\n".join(commands)
    if user_name:
        message = (
            f"👋 ברוך הבא שוב, <b>{user_name}</b>! "
            f"אני הבוט שלך למעקב אחר ציוד במחסן. \n\n"
            f"*מה תרצה לעשות?*\n"
            f"{commands_text}"
        )
        await update.message.reply_text(message, parse_mode="HTML")
    else:
        message = (
            f"👋 שלום *{user.first_name}*, ברוך הבא לזיוודיה! 🔫\n\n"
            f"🚨 *שים לב:* לפני שנוכל להתחיל, עליך לבחור שם קבוע שייצג אותך במערכת המעקב. "
            f"שם זה ישמש לרישום כל הפעולות שלך.\n\n"
            f"אנא התחל את תהליך ההרשמה באמצעות הפקודה:\n"
            f"*/register*"
        )
        await update.message.reply_text(message, parse_mode="Markdown")
    

async def daily_count_command (update: Update , context : ContextTypes.DEFAULT_TYPE ):
    def format_records_table(data):
        table = PrettyTable()
        table.field_names = ['קטגוריה' , 'כמות']
        for row in data:
            category,total_count , rest_count = row
            table.add_row([category,  f"{rest_count}/{total_count}"])
        return f"```\n{table.get_string()}\n```"

    data = get_inventory_summary()
    if not data:
        await update.message.reply_text("אין נתונים להצגה כרגע.")
        return
    final_message = format_records_table(data)
    await update.message.reply_text(f"* ספירה יומית*\n{final_message}" ,parse_mode="Markdown")

async def records_command(update: Update , context : ContextTypes.DEFAULT_TYPE ):
    def format_records_table(data):
        table = PrettyTable()
        table.field_names = ['פריט' , 'שם' , 'נלקח בתאריך']
        for row in data:
            item_id, name, date = row
            table.add_row([item_id, name , date])
        return f"```\n{table.get_string()}\n```"
    items = get_active_records()
    final_message = format_records_table(items)
    await update.message.reply_text(f"*לוח חתימות:*\n{final_message}" ,parse_mode="Markdown")


