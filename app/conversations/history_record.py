from telegram import Update
from telegram.ext import ContextTypes , ConversationHandler
from db.db import (get_history_by_time)
from db.test_db import create_table
from prettytable import PrettyTable
import re

ASK_DAYES= range(1)

def format_history_table(data):
    table = PrettyTable()
    table.field_names = ['פריט' , 'שם' , 'הוחזר?' ,'תאריך']
    for row in data:
        item_id, name, is_return_int, date = row
        is_return_text = "✅ כן" if is_return_int == 1 else "❌ לא"
        table.add_row([item_id, name, is_return_text, date])
    return f"```\n{table.get_string()}\n```"

async def get_history_command(update: Update , context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("כמה ימים אחורה תרצה לבדוק? (הקלד מספר שלם)")
    return ASK_DAYES

async def ask_days(update:Update , context : ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        days = int(text.strip())
        if days <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ הקלט אינו מספר ימים חוקי. אנא הקלד מספר שלם וחיובי.")
        return ASK_DAYES # חוזרים לשלב השאלה
    
        
    
    data = get_history_by_time(text)
    if not data:
        await update.message.reply_text(f"🔍 לא נמצאה היסטוריית רשומות ב-{days} הימים האחרונים.")
        return ConversationHandler.END
    table_message = format_history_table(data)


    await update.message.reply_text(f"*היסטוריית רשומות ב-{days} ימים אחרונים:*\n{table_message}", parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ הפעולה בוטלה.")
    return ConversationHandler.END