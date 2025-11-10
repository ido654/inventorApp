from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.db import register_user

ASK_DISPLAY_NAME = range(1)

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """מאתחל את תהליך ההרשמה."""
    await update.message.reply_text("👋 ברוך הבא לבוט הזיוודיה! לפני שנתחיל, אנא בחר **שם** שייצג אותך בכל הפעולות בבוט.")
    return ASK_DISPLAY_NAME

async def handle_registration_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """שומר את השם שבחר המשתמש."""
    display_name = update.message.text.strip()
    user_id = update.effective_user.id
    
    if not display_name or len(display_name) < 2 or len(display_name) > 30:
        await update.message.reply_text("❌ השם שבחרת לא תקין (חייב להיות בין 2 ל-30 תווים). נסה שוב.")
        return ASK_DISPLAY_NAME # נשארים באותו שלב
    
    # שומרים ב-DB
    register_user(user_id, display_name)
    
    await update.message.reply_text(f"✅ יפה מאוד, {display_name}! ההרשמה הושלמה. מעכשיו תזוהה בכינוי זה.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ הפעולה בוטלה.")
    return ConversationHandler.END