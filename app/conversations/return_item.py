from telegram import Update
from telegram.ext import ContextTypes , ConversationHandler
from db.db import (remove_record , get_record , get_user_display_name)
import re

ASK_ITEM_ID = range(1)

async def return_command(update: Update , context : ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    display_name = get_user_display_name(user_id)
    
    if not display_name:
        await update.message.reply_text("🚨 עליך להירשם תחילה! אנא השתמש בפקודת /register כדי להירשם.")
        return ConversationHandler.END
    
    context.user_data['name'] = display_name
    await update.message.reply_text(f"👋 {display_name}, איזה פריטים תרצה להחזיר?")
    return ASK_ITEM_ID

async def ask_items(update:Update , context : ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    name = context.user_data['name']
    item_ids = list(set(int(n) for n in re.findall(r'\d+', text)))
    
    if not item_ids:
        await update.message.reply_text("🤔 לא זיהיתי מזהי פריטים תקינים בהודעה. הפעולה בוטלה.")
        return ConversationHandler.END
    
    successful_return = []
    not_found = []


    for item_id in item_ids:
        status = remove_record(name, item_id)
        if status == "SUCCESS":
            successful_return.append(str(item_id))
        elif status == "NOT_TAKEN":
            not_found.append(str(item_id))
        

    messages = []
    if successful_return:
        messages.append(f"✅ החזרת בהצלחה : {', '.join(map(str, successful_return))}")
    if not_found:
        messages.append(f"❌ הפריטים {', '.join(not_found)} אינם חתומים.")
    await update.message.reply_text("\n".join(messages) or '🚫 לא בוצעה כל פעולה. ')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ הפעולה בוטלה.")
    return ConversationHandler.END