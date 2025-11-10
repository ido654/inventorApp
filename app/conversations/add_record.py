from telegram import Update
from telegram.ext import ContextTypes , ConversationHandler
from db.db import (add_record  , get_user_display_name)
import re


ASK_ITEM_ID = range(1)

async def new_record_command(update: Update , context : ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    display_name = get_user_display_name(user_id)
    
    if not display_name:
        await update.message.reply_text("🚨 עליך להירשם תחילה! אנא השתמש בפקודת /register כדי להירשם.")
        return ConversationHandler.END
    
    context.user_data['name'] = display_name
    await update.message.reply_text(f"👋 {display_name}, על איזה פריטים תרצה לחתום?")
    return ASK_ITEM_ID


async def ask_item_id(update:Update , context : ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    name = context.user_data['name']
    item_ids = list(set(int(n) for n in re.findall(r'\d+', text)))

    if not item_ids:
        await update.message.reply_text("🤔 לא זיהיתי מזהי פריטים תקינים בהודעה. הפעולה בוטלה.")
        return ConversationHandler.END 
    
    successful_takes = []
    takeovers = []
    not_found = []

    for item_id in item_ids:
        status = add_record(name, item_id)    
        if status == "SUCCESS":
            successful_takes.append(str(item_id))
        elif status == "TAKEOVER":
            takeovers.append(str(item_id))
        elif status  == "ITEM_NOT_FOUND":
            not_found.append(str(item_id))

    messages = []
    if successful_takes:
        messages.append(f"✅ {name} חתמת בהצלחה על הפריטים: {', '.join(successful_takes)}.")
    if takeovers:
        messages.append(f"⚠️ **החלפת חתימה:** {name} קיבל את האחריות על הפריטים: {', '.join(takeovers)} (החתימה הקודמת נסגרה).")
    if not_found:
        messages.append(f"❌ הפריטים {', '.join(not_found)} אינם קיימים במלאי.")


    
    await update.message.reply_text("\n".join(messages) or '🚫 לא בוצעה כל פעולה. ')

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ הפעולה בוטלה.")
    return ConversationHandler.END


